import os
from typing import List

from cachetools import TTLCache, cached
from collections import defaultdict
from flask_sqlalchemy_session import current_session
from sqlalchemy.orm import load_only
from sqlalchemy import distinct
from sqlalchemy.sql.functions import func

from billparser.db.models import (
    Congress,
    Legislation,
    LegislationContent,
    LegislationVersion,
    USCContentDiff,
    USCChapter,
    USCSection,
    Version,
    USCRelease,
    USCContent,
)
from congress_api.models.bill_metadata import BillMetadata  # noqa: E501
from congress_api.models.bill_text_content import BillTextContent  # noqa: E501
from congress_api.models.bill_text_response import BillTextResponse  # noqa: E501
from congress_api.models.bill_version_metadata import BillVersionMetadata  # noqa: E501
from congress_api.models.usc_section_content import USCSectionContent
from congress_api.models.bill_diff_list import BillDiffList, BillDiffMetadataItem
from congress_api.models.bill_content_diff import BillContentDiff  # noqa: E501
from congress_api.models.bill_content_diff_list import BillContentDiffList  # noqa: E501

CACHE_TIME = int(os.environ.get("CACHE_TIME", 0))
CACHE_SIZE = int(os.environ.get("CACHE_SIZE", 512))


@cached(TTLCache(CACHE_SIZE, CACHE_TIME))
def get_legislation_details(
    session_number: int, chamber: str, bill_number: int
) -> BillMetadata:
    chamber = chamber.lower()
    chamber = chamber[0].upper() + chamber[1:]

    bills = (
        current_session.query(Legislation)
        .filter(Congress.congress_id == Legislation.congress_id)
        .filter(Congress.session_number == session_number)
        .filter(Legislation.chamber == chamber)
        .filter(Legislation.number == bill_number)
        .order_by(Legislation.number)
        .options(
            load_only(
                Legislation.legislation_id,
                Legislation.title,
                Legislation.number,
                Legislation.congress_id,
                Legislation.legislation_type,
            )
        )
        .limit(1)
    )
    bills_results: List[Legislation] = bills.all()
    if len(bills_results) == 0:
        return None
    bill = bills_results[0]

    legis_versions = (
        current_session.query(LegislationVersion)
        .filter(LegislationVersion.legislation_id == bill.legislation_id)
        .options(
            load_only(
                LegislationVersion.legislation_version_id,
                LegislationVersion.legislation_version,
                LegislationVersion.effective_date,
                LegislationVersion.created_at,
            )
        )
        .order_by(LegislationVersion.effective_date)
        .all()
    )
    release_id = (
        current_session.query(USCRelease)
        .join(
            LegislationVersion,
            LegislationVersion.legislation_version_id
            == legis_versions[0].legislation_version_id,
        )
        .join(Version, USCRelease.version_id == Version.base_id)
        .filter(LegislationVersion.version_id == Version.version_id)
        .limit(1)
        .all()
    )
    result = BillMetadata(
        legislation_type=bill.legislation_type,
        congress=session_number,
        number=bill.number,
        title=bill.title,
        legislation_id=bill.legislation_id,
        legislation_versions=[],
        chamber=chamber,
        usc_release_id=release_id[0].usc_release_id,
    )
    for vers in legis_versions:
        result.legislation_versions.append(
            BillVersionMetadata(
                legislation_id=result.legislation_id,
                legislation_version_id=vers.legislation_version_id,
                effective_date=str(vers.effective_date),
                created_at=vers.created_at,
                legislation_version=vers.legislation_version,
            )
        )
    return result


@cached(TTLCache(CACHE_SIZE, CACHE_TIME))
def get_legislation_version_details(
    session_number: int, chamber, bill_number: int, legislation_version: str
) -> BillVersionMetadata:
    chamber = chamber.lower()
    chamber = chamber[0].upper() + chamber[1:]

    legislation_version = legislation_version.upper()
    bills = (
        current_session.query(Legislation)
        .filter(Congress.congress_id == Legislation.congress_id)
        .filter(Congress.session_number == session_number)
        .filter(Legislation.chamber == chamber)
        .filter(Legislation.number == bill_number)
        .order_by(Legislation.number)
        .options(
            load_only(
                Legislation.legislation_id,
                Legislation.title,
                Legislation.number,
                Legislation.congress_id,
                Legislation.legislation_type,
            )
        )
        .limit(1)
    )

    bills_results: List[Legislation] = bills.all()
    if len(bills_results) == 0:
        return None
    bill = bills_results[0]
    legis_versions = (
        current_session.query(LegislationVersion)
        .filter(LegislationVersion.legislation_id == bill.legislation_id)
        .filter(LegislationVersion.legislation_version == legislation_version)
        .options(
            load_only(
                LegislationVersion.legislation_version_id,
                LegislationVersion.legislation_version,
                LegislationVersion.effective_date,
                LegislationVersion.created_at,
            )
        )
        .order_by(LegislationVersion.effective_date)
        .limit(1)
        .all()
    )
    if len(legis_versions) == 0:
        return None

    vers = legis_versions[0]

    return BillVersionMetadata(
        legislation_id=bill.legislation_id,
        legislation_version_id=vers.legislation_version_id,
        effective_date=str(vers.effective_date),
        created_at=vers.created_at,
        legislation_version=vers.legislation_version,
    )


@cached(TTLCache(CACHE_SIZE, CACHE_TIME))
def get_legislation_version_text(
    session_number: int,
    chamber,
    bill_number: int,
    legislation_version: str,
    include_parsed: bool,
) -> BillTextResponse:
    chamber = chamber.lower()
    chamber = chamber[0].upper() + chamber[1:]

    legislation_version = legislation_version.upper()
    bills = (
        current_session.query(Legislation)
        .filter(Congress.congress_id == Legislation.congress_id)
        .filter(Congress.session_number == session_number)
        .filter(Legislation.chamber == chamber)
        .filter(Legislation.number == bill_number)
        .order_by(Legislation.number)
        .options(load_only(Legislation.legislation_id,))
        .limit(1)
    )

    bills_results: List[Legislation] = bills.all()
    if len(bills_results) == 0:
        return None

    bill = bills_results[0]
    legis_versions = (
        current_session.query(LegislationVersion)
        .filter(LegislationVersion.legislation_id == bill.legislation_id)
        .filter(LegislationVersion.legislation_version == legislation_version)
        .options(load_only(LegislationVersion.legislation_version_id,))
        .limit(1)
        .all()
    )
    if len(legis_versions) == 0:
        return None

    vers = legis_versions[0]

    text: List[LegislationContent] = (
        current_session.query(LegislationContent)
        .filter(
            LegislationContent.legislation_version_id == vers.legislation_version_id
        )
        .all()
    )

    diffs = (
        current_session.query(
            USCContentDiff.legislation_content_id,
            USCContentDiff.usc_ident,
            USCContent.usc_ident,
        )
        .join(USCContent, USCContentDiff.usc_content_id == USCContent.usc_content_id)
        .filter(
            USCContentDiff.legislation_content_id.in_(
                [x.legislation_content_id for x in text]
            )
        )
        .all()
    )

    def get_shortest(str1, str2):
        if str1 == "":
            return str2
        if len(str1) < len(str2):
            return str1
        return str2

    diff_lookup = {}
    for (lci, u1, u2) in diffs:
        diff_lookup[lci] = get_shortest(diff_lookup.get(lci, ""), u1 or u2 or "")
    return BillTextResponse(
        legislation_id=bill.legislation_id,
        legislation_version_id=vers.legislation_version_id,
        legislation_version=vers.legislation_version,
        content=[
            BillTextContent(
                legislation_content_id=t.legislation_content_id,
                parent_id=t.parent_id,
                order_number=t.order_number,
                section_display=t.section_display,
                heading=t.heading,
                content_str=t.content_str,
                content_type=t.content_type,
                action=[
                    {**x, "cite_link": diff_lookup.get(t.legislation_content_id)}
                    for x in t.action_parse
                ]
                if include_parsed
                else [],
                lc_ident=t.lc_ident,
            )
            for (t) in text
        ],
    )


def get_legislation_version_diffs(
    session_number, chamber, bill_number, version, short_title, section_number
) -> BillContentDiffList:
    chamber = chamber.lower()
    chamber = chamber[0].upper() + chamber[1:]

    version = version.upper()
    bills = (
        current_session.query(Legislation)
        .filter(Congress.congress_id == Legislation.congress_id)
        .filter(Congress.session_number == session_number)
        .filter(Legislation.chamber == chamber)
        .filter(Legislation.number == bill_number)
        .order_by(Legislation.number)
        .options(load_only(Legislation.legislation_id,))
        .limit(1)
    )

    bills_results: List[Legislation] = bills.all()
    if len(bills_results) == 0:
        return None

    bill = bills_results[0]
    legis_versions = (
        current_session.query(LegislationVersion)
        .filter(LegislationVersion.legislation_id == bill.legislation_id)
        .filter(LegislationVersion.legislation_version == version)
        .options(
            load_only(
                LegislationVersion.version_id, LegislationVersion.legislation_version_id
            )
        )
        .limit(1)
        .all()
    )

    if len(legis_versions) == 0:
        return None

    diffs = (
        current_session.query(USCContentDiff)
        .join(USCSection, USCSection.number == section_number)
        .join(USCChapter, USCChapter.short_title == short_title)
        .filter(USCChapter.usc_chapter_id == USCSection.usc_chapter_id)
        .filter(USCContentDiff.version_id == legis_versions[0].version_id)
        .filter(USCContentDiff.usc_section_id == USCSection.usc_section_id)
        .all()
    )
    return BillContentDiffList(
        legislation_version_id=legis_versions[0].legislation_version_id,
        diffs=[
            BillContentDiff(
                number=x.number,
                content_type=x.content_type,
                content_str=x.content_str,
                heading=x.heading,
                section_display=x.section_display,
                order_number=x.order_number,
                usc_guid=x.usc_guid,
                usc_ident=x.usc_ident,
                usc_content_id=x.usc_content_id,
                usc_section_id=x.usc_section_id,
                usc_content_diff_id=x.usc_content_diff_id,
            )
            for x in diffs
        ],
    )


@cached(TTLCache(CACHE_SIZE, CACHE_TIME))
def get_legislation_version_diff_metadata(
    session_number, chamber, bill_number, version
) -> BillMetadata:
    chamber = chamber.lower()
    chamber = chamber[0].upper() + chamber[1:]

    version = version.upper()
    bills = (
        current_session.query(Legislation)
        .filter(Congress.congress_id == Legislation.congress_id)
        .filter(Congress.session_number == session_number)
        .filter(Legislation.chamber == chamber)
        .filter(Legislation.number == bill_number)
        .order_by(Legislation.number)
        .options(load_only(Legislation.legislation_id,))
        .limit(1)
    )

    bills_results: List[Legislation] = bills.all()
    if len(bills_results) == 0:
        return None

    bill = bills_results[0]
    legis_versions = (
        current_session.query(LegislationVersion)
        .filter(LegislationVersion.legislation_id == bill.legislation_id)
        .filter(LegislationVersion.legislation_version == version)
        .options(
            load_only(
                LegislationVersion.version_id, LegislationVersion.legislation_version_id
            )
        )
        .limit(1)
        .all()
    )

    if len(legis_versions) == 0:
        return None

    diff_sections = list(
        current_session.execute(
            f"""
SELECT DISTINCT usc_chapter.short_title, usc_chapter.long_title, usc_section.number, usc_section.heading, usc_section.section_display
  FROM public.usc_content_diff
  JOIN usc_chapter ON usc_chapter.usc_chapter_id = usc_content_diff.usc_chapter_id
  JOIN usc_section ON usc_content_diff.usc_section_id = usc_section.usc_section_id
  WHERE usc_content_diff.version_id = {legis_versions[0].version_id} ORDER BY usc_chapter.short_title, usc_section.number;
;
"""
        )
    )
    res = defaultdict(list)
    for row in diff_sections:
        res[row[0]].append(
            BillDiffMetadataItem(
                long_title=row[1],
                section_number=row[2],
                heading=row[3],
                display=row[4],
            )
        )
    ret = []
    for (key, value) in res.items():
        ret.append(
            BillDiffList(
                legislation_version_id=legis_versions[0].legislation_version_id,
                short_title=key,
                long_title=value[0].long_title,
                sections=value,
            )
        )
    return sorted(ret, key=lambda x: x.short_title)
