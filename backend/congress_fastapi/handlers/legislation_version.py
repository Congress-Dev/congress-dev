from typing import List

from sqlalchemy import select

from congress_fastapi.db.postgres import get_database
from billparser.db.models import (
    LegislationContentTag,
    LegislationContent,
    LegislationContentSummary,
    Legislation,
    LegislationVersion,
    Congress,
)

from congress_fastapi.models.legislation import (
    LegislationClauseTag,
    LegislationClauseSummary,
    LegislationVersionMetadata,
)


async def get_legislation_version_tags_by_legislation_id(
    legislation_version_id: int,
) -> List[LegislationClauseTag]:
    database = await get_database()
    query = (
        select(
            *LegislationClauseTag.sqlalchemy_columns(),
        )
        .select_from(LegislationContent)
        .where(LegislationContent.legislation_version_id == legislation_version_id)
        .join(
            LegislationContentTag,
            LegislationContentTag.legislation_content_id
            == LegislationContent.legislation_content_id,
        )
        .order_by(LegislationContentTag.legislation_content_id)
    )
    results = list(await database.fetch_all(query))
    if results is None or len(results) == 0:
        return None
    return [
        LegislationClauseTag.from_sqlalchemy(result) for result in results if result
    ]


async def get_legislation_version_summaries_by_legislation_id(
    legislation_version_id: int,
) -> List[LegislationClauseSummary]:
    database = await get_database()
    query = (
        select(
            *LegislationClauseSummary.sqlalchemy_columns(),
        )
        .select_from(LegislationContent)
        .where(LegislationContent.legislation_version_id == legislation_version_id)
        .join(
            LegislationContentSummary,
            LegislationContentSummary.legislation_content_id
            == LegislationContent.legislation_content_id,
        )
        .order_by(LegislationContentSummary.legislation_content_id)
    )
    results = list(await database.fetch_all(query))
    if results is None or len(results) == 0:
        return None
    return [
        LegislationClauseSummary.from_sqlalchemy(result) for result in results if result
    ]





async def get_legislation_version_summaries_by_bill_number(
    congress_session_number: int,
    chamber: str,
    bill: int,
    version_id: str,
) -> List[LegislationVersionMetadata]:
    database = await get_database()
    query = (
        select(
            *LegislationVersionMetadata.sqlalchemy_columns(),
        )
        .select_from(LegislationVersion)
        .where(LegislationVersion.legislation_version == version_id)
        .join(
            Legislation,
            Legislation.legislation_id
            == LegislationVersion.legislation_id,
        )
        .where(Legislation.number == bill, Legislation.chamber == chamber)
        .join(
            Congress,
            Congress.congress_id == Legislation.congress_id
            )
        .where(Congress.session_number == congress_session_number)
        .order_by(LegislationVersion.created_at.desc())
        .limit(1)
    )
    print(query)
    results = list(await database.fetch_all(query))
    if results is None or len(results) == 0:
        return None
    return [
        LegislationVersionMetadata.from_sqlalchemy(result) for result in results if result
    ]





'''
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

'''