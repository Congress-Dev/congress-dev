from flask_sqlalchemy_session import current_session
from billparser.db.models import (
    USCChapter,
    USCSection,
    USCContent,
    USCContentDiff,
    Legislation,
    LegislationVersion,
    LegislationContent,
    LegislationChamber,
    LegislationVersionEnum,
    LegislationActionParse,
    Version,
)
from cachetools import cached, TTLCache
from sqlalchemy import or_, String, func
from sqlalchemy.sql.expression import cast
from sqlalchemy.sql import alias
import re

from typing import Dict, List

import platform

windows = platform.system() == "Windows"

DEFAULT_VERSION_ID = 1
CACHE_TIME = 600

if windows:
    CACHE_TIME = 0


@cached(cache=TTLCache(maxsize=512, ttl=CACHE_TIME))
def get_chapters(version_id=DEFAULT_VERSION_ID) -> List[USCChapter]:
    """
    Gets all the Chapters for the current version

    Returns:
        List[USCChapter]: A list of all the
    """
    latest_base = get_latest_base()
    results = (
        current_session.query(USCChapter)
        .filter(USCChapter.version_id == latest_base.version_id)
        .all()
    )
    return results


@cached(cache=TTLCache(maxsize=512, ttl=CACHE_TIME))
def get_bills(
    house: int, senate: int, query: str, incl: str, decl: str
) -> List[Legislation]:
    """
    Gets the Bill rows according to the filters.

    Args:
        house (int): Include House bills
        senate (int): Include Senate bills
        query (str): Text to search for in the title
        incl (str): Versions to include
        decl (str): Versions to exclude

    Returns:
        List[Legislation]: Bill objects that pass the above filters
    """
    results = current_session.query(Legislation).join(LegislationVersion)
    if house != 1:
        results = results.filter(Legislation.chamber != LegislationChamber.House)
    if senate != 1:
        results = results.filter(Legislation.chamber != LegislationChamber.Senate)
    if len(query) > 0:
        results = results.filter(
            or_(
                Legislation.title.ilike(f"%{query}%"),
                cast(Legislation.number, String).like(
                    re.sub(r"[^0-9\s]", "", query).strip()
                ),
            )
        )
    if incl != "":
        incl_set = [
            LegislationVersionEnum(x.upper())
            for x in incl.split(",")
            if x.upper() in LegislationVersionEnum.__members__
        ]
        results = results.filter(LegislationVersion.legislation_version.in_(incl_set))
    if decl != "":
        decl_set = [
            LegislationVersionEnum(x.upper())
            for x in decl.split(",")
            if x.upper() in LegislationVersionEnum.__members__
        ]
        results = results.filter(~LegislationVersion.legislation_version.in_(decl_set))
    results = results.order_by(Legislation.number).limit(100).all()
    return results


@cached(cache=TTLCache(maxsize=512, ttl=CACHE_TIME))
def get_versions() -> List[Version]:
    """
    Gets a list of all the Version rows that correspond to Bills

    Returns:
        List[Version]: List of Versions corresponding to the Bill versions
    """
    results = current_session.query(Version).filter(Version.base_id is not None).all()
    return results


@cached(cache=TTLCache(maxsize=512, ttl=CACHE_TIME))
def get_revisions() -> List[Version]:
    """
    Gets a list of all the Version rows that correspond to USCode revisions

    Returns:
        List[Version]: List of Versions that are USCode revisions
    """
    results = current_session.query(Version).filter(Version.base_id is None).all()
    return results


@cached(cache=TTLCache(maxsize=512, ttl=CACHE_TIME))
def get_latest_sections(chapter_number: str) -> List[USCSection]:
    """
    Gets the sections for the given Chapter, from the first USCode revision in the table

    Args:
        chapter_number (str): Given Chapter.number to look for

    Returns:
        List[USCSection]: List of Sections from the given Chapter
    """
    latest_base = (
        current_session.query(Version).filter(Version.base_id == None).all()[0]
    )
    chapter = (
        current_session.query(USCChapter)
        .filter(USCChapter.version_id == latest_base.version_id)
        .filter(USCChapter.short_title == chapter_number)
        .first()
    )
    results = (
        current_session.query(USCSection)
        .filter(USCSection.usc_chapter_id == chapter.usc_chapter_id)
        .all()
    )
    return results


@cached(cache=TTLCache(maxsize=512, ttl=CACHE_TIME))
def get_sections(chapter_id: int, version_id: int) -> List[USCSection]:
    """
    Gets the sections from the chapter and version id

    Args:
        chapter_id (int): Chapter id to look at
        version_id (int): Version id to look at

    Returns:
        List[USCSection]: List of sections that match the criteria
    """
    results = (
        current_session.query(USCSection)
        .filter(
            USCSection.usc_chapter_id == chapter_id, USCSection.version_id == version_id
        )
        .all()
    )
    return results


@cached(cache=TTLCache(maxsize=512, ttl=CACHE_TIME))
def get_latest_content(chapter_number: str, section_number: str) -> List[USCContent]:
    """
    Converts a chapter number and section number into chapter and version ids
    Then calls the get_content function with those arguments

    Args:
        chapter_number (str): The Chapter number to search for
        section_number (str): The Section number to search for

    Returns:
        List[USCContent]: List of Contents from the given section
    """
    latest_base = get_latest_base()
    chapter = (
        current_session.query(USCChapter)
        .filter(USCChapter.version_id == latest_base.version_id)
        .filter(USCChapter.short_title == chapter_number)
        .first()
    )
    section = (
        current_session.query(USCSection)
        .filter(USCSection.version_id == latest_base.version_id)
        .filter(USCSection.number == section_number)
        .filter(USCSection.usc_chapter_id == chapter.usc_chapter_id)
        .first()
    )
    return get_content(section.usc_section_id, latest_base.version_id)


@cached(cache=TTLCache(maxsize=512, ttl=CACHE_TIME))
def get_content(section_id: int, version_id: int) -> List[USCContent]:
    """
    Gets the contents of a given Section in a given Version

    TODO: Is version id redundent here?

    Args:
        section_id (int): Section id to look at
        version_id (int): Version id to look at

    Returns:
        List[USCContent]: Content that passes the above filter
    """
    results = (
        current_session.query(USCContent)
        .filter(
            USCContent.usc_section_id == section_id, USCContent.version_id == version_id
        )
        .order_by(USCContent.order_number.asc())
        .all()
    )
    return results


# TODO: Need to fix
@cached(cache=TTLCache(maxsize=512, ttl=CACHE_TIME))
def get_content_versions(bill_version_id: int) -> List[USCContent]:
    """
    Returns the content versions for a given bill version id

    Args:
        bill_version_id (int): Given bill version id

    Returns:
        List[Content]: List of Content that corresponds to a given Bill
    """
    results = (
        current_session.query(USCContent)
        .filter(
            USCContent.version_id == bill_version_id,
        )
        .all()
    )
    return results


@cached(cache=TTLCache(maxsize=512, ttl=CACHE_TIME))
def get_diffs(bill_version_id: int) -> List[USCContentDiff]:
    """
    Gets the USCContentDiff for a given bill_version_id

    Args:
        bill_version_id (int): Target bill version id

    Returns:
        List[USCContentDiff]: List of USCContentDiff for the bill version
    """
    legis_vers = (
        current_session.query(LegislationVersion)
        .filter(LegislationVersion.legislation_version_id == bill_version_id)
        .all()
    )
    if len(legis_vers) == 0:
        return []
    results = (
        current_session.query(USCContentDiff)
        .filter(USCContentDiff.version_id == legis_vers[0].version_id)
        .all()
    )
    return results


@cached(cache=TTLCache(maxsize=512, ttl=CACHE_TIME))
def get_bill_contents(bill_version_id: int) -> List[LegislationContent]:
    """
    Returns the LegislationContent for a given bill_version

    Args:
        bill_version_id (int): LegislationContent PK on the LegislationContent table

    Returns:
        List[LegislationContent]: Matching LegislationContent rows
    """
    results = (
        current_session.query(LegislationContent)
        .filter(LegislationContent.legislation_version_id == bill_version_id)
        .all()
    )
    return results


@cached(cache=TTLCache(maxsize=512, ttl=CACHE_TIME))
def get_bill_metadata(bill_version_id: int) -> dict:
    bill_version = (
        current_session.query(LegislationVersion)
        .filter(LegislationVersion.legislation_version_id == bill_version_id)
        .all()
    )
    if len(bill_version) > 0:
        bill = (
            current_session.query(Legislation)
            .filter(Legislation.legislation_id == bill_version[0].legislation_id)
            .all()
        )
        if len(bill) > 0:
            return {
                "chamber": bill[0].chamber.value,
                "number": bill[0].number,
                "version": bill_version[0].legislation_version.value.lower(),
            }

    return {}


def get_revision_diff(base_id: int, new_id: int):
    # Gets the diffs between two versions
    # SELECT t1.section_id as old_s_id, t2.section_id as new_s_id, t1.usc_ident, t1.section_display as old_s_d, t2.section_display as new_s_d, t1.heading, t2.heading FROM sections as t1 JOIN sections as t2 ON t2.version_id = 2 WHERE t1.version_id = 1 AND t1.usc_ident = t2.usc_ident AND (t1.heading != t2.heading) LIMIT 5000;
    new_sections: Section = Section.alias("new")
    old_sections: Section = Section.alias("old")
    results = (
        current_session.query(new_sections.usc_section_id, old_sections.usc_section_id)
        .join(old_sections, old_sections.version_id == new_id)
        .filter(new_sections.version_id == base_id)
        .filter(old_sections.usc_ident == new_sections.usc_ident)
        .filter(old_sections.heading != new_sections.heading)
    ).all()
    return results


def get_latest_base() -> Version:
    try:
        return current_session.query(Version).filter(Version.base_id == None).all()[0]
    except Exception:
        return None


def check_for_action_parses(legislation_version_id: List[int]) -> Dict[int, int]:
    """
    Return a dict of the number of action parses for each legislation_version_id
    """

    results = (
        current_session.query(
            LegislationActionParse.legislation_version_id,
            func.count(LegislationActionParse.legislation_action_parse_id),
        )
        .filter(
            LegislationActionParse.legislation_version_id.in_(legislation_version_id)
        )
        .group_by(LegislationActionParse.legislation_version_id)
        .all()
    )
    return {x[0]: x[1] for x in results}


def get_legislation_versions() -> List[LegislationVersion]:
    """
    Returns a list of all legislation_version_ids
    """
    results = current_session.query(LegislationVersion).all()
    return [x[0] for x in results]