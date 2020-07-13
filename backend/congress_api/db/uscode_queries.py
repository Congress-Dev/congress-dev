import os
from typing import List

from cachetools import TTLCache, cached
from flask_sqlalchemy_session import current_session
from sqlalchemy import desc

from billparser.db.models import USCChapter, USCContent, USCRelease, USCSection
from congress_api.models.release_point_list import ReleasePointList
from congress_api.models.release_point_metadata import ReleasePointMetadata
from congress_api.models.usc_section_content import USCSectionContent
from congress_api.models.usc_section_content_list import USCSectionContentList
from congress_api.models.usc_section_list import USCSectionList
from congress_api.models.usc_section_metadata import USCSectionMetadata
from congress_api.models.usc_title_list import USCTitleList
from congress_api.models.usc_title_metadata import USCTitleMetadata

CACHE_TIME = int(os.environ.get("CACHE_TIME", 0))
CACHE_SIZE = int(os.environ.get("CACHE_SIZE", 512))


@cached(TTLCache(CACHE_SIZE, CACHE_TIME))
def _get_latest_rp() -> USCRelease:
    rp = (
        current_session.query(USCRelease)
        .order_by(desc(USCRelease.effective_date))
        .all()
    )
    if len(rp) > 0:
        return rp[0]
    return None


@cached(TTLCache(CACHE_SIZE, CACHE_TIME))
def _get_title_obj(release_id: int, short_title: str) -> USCChapter:
    chap = (
        current_session.query(USCChapter)
        .filter(USCChapter.usc_release_id == release_id)
        .filter(USCChapter.short_title == short_title)
        .all()
    )
    if len(chap) > 0:
        return chap[0]
    return None


@cached(TTLCache(CACHE_SIZE, CACHE_TIME))
def _get_sect_obj(chapter_id: int, section_number: str) -> USCSection:
    sect = (
        current_session.query(USCSection)
        .filter(USCSection.usc_chapter_id == chapter_id)
        .filter(USCSection.number == section_number)
        .filter(USCSection.content_type == 'section')
        .all()
    )
    if len(sect) > 0:
        return sect[0]
    return None


@cached(TTLCache(CACHE_SIZE, CACHE_TIME))
def get_available_releases() -> ReleasePointList:
    rp: List[USCRelease] = current_session.query(USCRelease).all()
    rp_models = []
    for point in rp:
        rp_models.append(
            ReleasePointMetadata(
                usc_release_id=point.usc_release_id,
                short_title=point.short_title,
                long_title=point.long_title,
                effective_date=point.effective_date,
            )
        )
    return ReleasePointList(releases=rp_models)


@cached(TTLCache(CACHE_SIZE, CACHE_TIME))
def get_available_titles(release_vers: str) -> USCTitleList:
    if release_vers.lower() == "latest":
        latest_rp = _get_latest_rp()
        if latest_rp is None:
            return None
        target_rp_id = latest_rp.usc_release_id
    else:
        target_rp_id = int(release_vers)

    titles: List[USCChapter] = current_session.query(USCChapter).filter(
        USCChapter.usc_release_id == target_rp_id
    ).all()
    rp_titles = []
    for chap in titles:
        rp_titles.append(
            USCTitleMetadata(
                usc_chapter_id=chap.usc_chapter_id,
                usc_release_id=target_rp_id,
                short_title=chap.short_title,
                long_title=chap.long_title,
            )
        )
    return USCTitleList(titles=rp_titles)


@cached(TTLCache(CACHE_SIZE, CACHE_TIME))
def get_title_sections(release_vers: str, short_title: str) -> USCSectionList:
    if release_vers.lower() == "latest":
        latest_rp = _get_latest_rp()
        if latest_rp is None:
            return None
        target_rp_id = latest_rp.usc_release_id
    else:
        target_rp_id = int(release_vers)

    title_obj = _get_title_obj(target_rp_id, short_title)
    if title_obj is None:
        return None

    sections: List[USCSection] = current_session.query(USCSection).filter(
        USCSection.usc_chapter_id == title_obj.usc_chapter_id
    ).filter(
        USCSection.content_type == "section"
    ).all()
    sect_list = []
    for sect in sections:
        sect_list.append(
            USCSectionMetadata(
                usc_section_id=sect.usc_section_id,
                usc_ident=sect.usc_ident,
                number=sect.number,
                section_display=sect.section_display,
                heading=sect.heading,
                usc_chapter_id=title_obj.usc_chapter_id,
                parent_id=sect.parent_id,
                content_type=sect.content_type,
            )
        )
    return USCSectionList(usc_chapter_id=title_obj.usc_chapter_id, sections=sect_list)


@cached(TTLCache(CACHE_SIZE, CACHE_TIME))
def get_section_text(
    release_vers: str, short_title: str, section_number: str
) -> USCSectionContentList:
    if release_vers.lower() == "latest":
        latest_rp = _get_latest_rp()
        if latest_rp is None:
            return None
        target_rp_id = latest_rp.usc_release_id
    else:
        target_rp_id = int(release_vers)

    title_obj = _get_title_obj(target_rp_id, short_title)
    if title_obj is None:
        return None

    sect_obj = _get_sect_obj(title_obj.usc_chapter_id, section_number)
    if sect_obj is None:
        return None

    content: List[USCContent] = current_session.query(USCContent).filter(
        USCContent.usc_section_id == sect_obj.usc_section_id
    ).all()

    cont_list = []
    for cont in content:
        cont_list.append(
            USCSectionContent(
                usc_content_id=cont.usc_content_id,
                usc_ident=cont.usc_ident,
                parent_id=cont.parent_id,
                order_number=cont.order_number,
                section_display=cont.section_display,
                heading=cont.heading,
                content_str=cont.content_str,
                content_type=cont.content_type,
                number=cont.number,
                usc_section_id=cont.usc_section_id,
            )
        )
    return USCSectionContentList(
        usc_section_id=sect_obj.usc_section_id, content=cont_list
    )

@cached(TTLCache(CACHE_SIZE, CACHE_TIME))
def get_section_levels(release_vers: str, short_title: str, section_id: int = None) -> USCSectionList:
    print(release_vers, short_title, section_id)
    if release_vers.lower() == "latest":
        latest_rp = _get_latest_rp()
        if latest_rp is None:
            return None
        target_rp_id = latest_rp.usc_release_id
    else:
        target_rp_id = int(release_vers)

    title_obj = _get_title_obj(target_rp_id, short_title)
    if title_obj is None:
        return None
    sections: List[USCSection] = current_session.query(USCSection).filter(
        USCSection.usc_chapter_id == title_obj.usc_chapter_id
    )
    if section_id not in [None, ' ', '']:
        sections = sections.filter(USCSection.parent_id == int(section_id))
    else:
        sections = sections.filter(USCSection.parent_id == None)
    sections = sections.all()

    sect_list = []
    for sect in sections:
        sect_list.append(
            USCSectionMetadata(
                usc_section_id=sect.usc_section_id,
                usc_ident=sect.usc_ident,
                number=sect.number,
                section_display=sect.section_display,
                heading=sect.heading,
                usc_chapter_id=title_obj.usc_chapter_id,
                parent_id=sect.parent_id,
                content_type=sect.content_type,
            )
        )
    return USCSectionList(usc_chapter_id=title_obj.usc_chapter_id, sections=sect_list)