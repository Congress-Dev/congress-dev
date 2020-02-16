import os
from typing import List

from cachetools import TTLCache, cached
from flask_sqlalchemy_session import current_session
from sqlalchemy.orm import load_only

from billparser.db.models import (
    Congress,
    Legislation,
    LegislationContent,
    LegislationVersion,
)
from congress_api.models.bill_metadata import BillMetadata  # noqa: E501
from congress_api.models.bill_text_content import BillTextContent  # noqa: E501
from congress_api.models.bill_text_response import BillTextResponse  # noqa: E501
from congress_api.models.bill_version_metadata import BillVersionMetadata  # noqa: E501

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
    result = BillMetadata(
        legislation_type=bill.legislation_type,
        congress=session_number,
        number=bill.number,
        title=bill.title,
        legislation_id=bill.legislation_id,
        legislation_versions=[],
        chamber=chamber,
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
                action=t.action_parse if include_parsed else [],
            )
            for t in text
        ],
    )
