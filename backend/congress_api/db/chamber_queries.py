import os
import re
from typing import List

from cachetools import TTLCache, cached
from flask_sqlalchemy_session import current_session
from sqlalchemy import String, or_
from sqlalchemy.orm import load_only
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.expression import cast

from billparser.db.models import (
    Congress,
    Legislation,
    LegislationChamber,
    LegislationVersion,
    LegislationVersionEnum,
)
from congress_api.models.bill_metadata import BillMetadata  # noqa: E501
from congress_api.models.bill_search_list import BillSearchList
from congress_api.models.bill_slim_metadata import BillSlimMetadata
from congress_api.models.bill_version_metadata import BillVersionMetadata  # noqa: E501
from congress_api.models.chamber_metadata import ChamberMetadata  # noqa: E501

CACHE_TIME = int(os.environ.get("CACHE_TIME", 0))
CACHE_SIZE = int(os.environ.get("CACHE_SIZE", 512))


@cached(TTLCache(CACHE_SIZE, CACHE_TIME))
def get_chamber_summary_obj(session_number: int, chamber: str) -> ChamberMetadata:
    """
    Queries for the Chamber summary for a given session of congress

    Args:
        session_number (int): The requested session
        chamber (str): The requested Chamber (House or Senate)

    Raises:
        TypeError: Raised when the session isn't a number

    Returns:
        ChamberMetadata: The number of bills loaded
    """
    if not isinstance(session_number, int):
        raise TypeError

    chamber = chamber.lower()
    chamber = chamber[0].upper() + chamber[1:]

    query = (
        current_session.query(
            Legislation.congress_id, func.count(Legislation.legislation_id)
        )
        .filter(Congress.congress_id == Legislation.congress_id)
        .filter(Congress.session_number == session_number)
        .filter(Legislation.chamber == chamber)
        .group_by(Legislation.congress_id)
    )
    results = query.all()
    if len(results) > 0:
        return ChamberMetadata(
            congress_id=results[0][0], bill_count=results[0][1], chamber=chamber
        )
    return None


@cached(TTLCache(CACHE_SIZE, CACHE_TIME))
def get_chamber_bills_list(
    session_number: int, chamber: str, page_size: int, page: int
) -> List[BillSlimMetadata]:
    if not isinstance(session_number, int):
        raise TypeError
    page_size = min(max(page_size, 1), 25)
    page = page - 1
    chamber = chamber.lower()
    chamber = chamber[0].upper() + chamber[1:]

    bills = (
        current_session.query(Legislation)
        .filter(Congress.congress_id == Legislation.congress_id)
        .filter(Congress.session_number == session_number)
        .filter(Legislation.chamber == chamber)
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
        .limit(page_size)
        .offset(page * page_size)
    )
    bills_results: List[Legislation] = bills.all()
    legis_id = []
    slim_bills = {}
    for bill in bills_results:
        legis_id.append(bill.legislation_id)
        slim_bills[bill.legislation_id] = BillSlimMetadata(
            legislation_id=bill.legislation_id,
            title=bill.title,
            number=bill.number,
            congress=session_number,
            legislation_type=bill.legislation_type.value,
            legislation_versions=[],
            chamber=chamber,
        )

    legis_versions = (
        current_session.query(LegislationVersion)
        .filter(LegislationVersion.legislation_id.in_(legis_id))
        .options(
            load_only(
                LegislationVersion.legislation_id,
                LegislationVersion.legislation_version,
            )
        )
        .all()
    )

    for vers in legis_versions:
        slim_bills[vers.legislation_id].legislation_versions.append(
            vers.legislation_version.value
        )
    return sorted(list(slim_bills.values()), key=lambda x: x.legislation_id)


@cached(TTLCache(CACHE_SIZE, CACHE_TIME))
def search_legislation(
    congress: str, chamber: str, versions: str, text: str, page: int, page_size: int
):

    if chamber not in ["None", "", None]:
        chambers = chamber.replace(" ", "").lower().split(",")
    else:
        chambers = []

    if congress in [None, "", "None"]:
        sessions = []
    else:
        sessions = congress.replace(" ", "").split(",")
    if versions not in ["", "None", None]:
        version_strs = versions.replace(" ", "").split(",")
    else:
        version_strs = []
    chamber_srch = []
    version_srch = []
    if "house" in chambers:
        chamber_srch.append(LegislationChamber.House)
    if "senate" in chambers:
        chamber_srch.append(LegislationChamber.Senate)
    for vers in version_strs:
        if vers.upper() in LegislationVersionEnum._member_names_:
            version_srch.append(LegislationVersionEnum(vers.upper()))
    if sessions != []:
        cong_query = (
            current_session.query(Congress)
            .filter(Congress.session_number.in_([int(x) for x in sessions]))
            .options(load_only(Congress.congress_id, Congress.session_number))
            .all()
        )
    else:
        cong_query = (
            current_session.query(Congress)
            .options(load_only(Congress.congress_id, Congress.session_number))
            .all()
        )
    congresses = {cong.congress_id: cong.session_number for cong in cong_query}
    query = current_session.query(Legislation)
    query = query.filter(Legislation.congress_id.in_(list(congresses.keys())))
    if chambers != []:
        query = query.filter(Legislation.chamber.in_(chamber_srch))
    query = query.filter(
        or_(
            Legislation.title.ilike(f"%{text}%"),
            cast(Legislation.number, String).like(
                re.sub(r"[^0-9\s]", "", text).strip()
            ),
        )
    )
    query = query.join(LegislationVersion)
    query = query.filter(LegislationVersion.legislation_version.in_(version_srch))
    query = query.order_by(Legislation.number)
    query = query.limit(int(page_size)).offset(int((page - 1) * page_size))
    query = query.options(
        load_only(
            Legislation.legislation_id,
            Legislation.title,
            Legislation.number,
            Legislation.congress_id,
            Legislation.legislation_type,
            Legislation.chamber,
        )
    )

    bills_results: List[Legislation] = query.all()

    if len(bills_results) == 0:
        return BillSearchList(params=None, legislation=[])

    bill_ids = [x.legislation_id for x in bills_results]

    legis_versions = (
        current_session.query(LegislationVersion)
        .filter(LegislationVersion.legislation_version.in_(version_srch))
        .filter(LegislationVersion.legislation_id.in_(bill_ids))
        .options(
            load_only(
                LegislationVersion.legislation_id,
                LegislationVersion.legislation_version_id,
                LegislationVersion.legislation_version,
                LegislationVersion.effective_date,
                LegislationVersion.created_at,
            )
        )
        .order_by(LegislationVersion.effective_date)
        .all()
    )

    bill_metadatas = []
    for bill in bills_results:
        result = BillMetadata(
            legislation_type=bill.legislation_type,
            congress=congresses[bill.congress_id],
            number=bill.number,
            title=bill.title,
            legislation_id=bill.legislation_id,
            legislation_versions=[],
            chamber=bill.chamber,
        )
        for vers in legis_versions:
            if vers.legislation_id != bill.legislation_id:
                continue
            result.legislation_versions.append(
                BillVersionMetadata(
                    legislation_id=result.legislation_id,
                    legislation_version_id=vers.legislation_version_id,
                    effective_date=str(vers.effective_date),
                    created_at=vers.created_at,
                    legislation_version=vers.legislation_version,
                )
            )
        if(len(result.legislation_versions) > 0):
            bill_metadatas.append(result)
    return BillSearchList(params=None, legislation=bill_metadatas)
