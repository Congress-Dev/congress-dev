from collections import defaultdict
from typing import Dict, List, Tuple

from sqlalchemy import select, join, func, distinct, exists
from sqlalchemy.orm import aliased
from congress_fastapi.db.postgres import get_database
from billparser.db.models import (
    Appropriation,
    Congress,
    Legislation,
    LegislationChamber,
    LegislationContent,
    LegislationContentSummary,
    LegislationContentTag,
    LegislationSponsorship,
    LegislationVersion,
    LegislationVersionEnum,
    Legislator,
)
from congress_fastapi.models.legislation.metadata import (
    LegislatorMetadata,
)
from congress_fastapi.models.legislation.search import SearchResult


def normalize_tags(tags: List[str]) -> List[str]:
    # Convert everything to title case
    # Replace underscores with spaces
    # Remove any leading or trailing whitespace
    return list(
        set(
            [
                tag.replace("_", " ").replace(" and ", " & ").strip().title()
                for tag in tags
            ]
        )
    )


async def get_distinct_tags(legislation_ids: List[int]) -> Dict[int, List[str]]:
    database = await get_database()

    # Subquery to get the highest legislation_version_id for each legislation_id
    subquery = (
        select(
            LegislationVersion.legislation_id,
            func.max(LegislationVersion.legislation_version_id).label("max_version_id"),
        )
        .group_by(LegislationVersion.legislation_id)
        .subquery()
    )

    # Aliases for the tables
    lv_alias = aliased(LegislationVersion)
    lct_alias = aliased(LegislationContentTag)
    lc_alias = aliased(LegislationContent)

    # Main query to get distinct tags
    query = (
        select(Legislation.legislation_id, lct_alias.tags)
        .select_from(
            join(
                Legislation,
                subquery,
                Legislation.legislation_id == subquery.c.legislation_id,
            )
            .join(
                lv_alias, lv_alias.legislation_version_id == subquery.c.max_version_id
            )
            .join(
                lc_alias,
                lv_alias.legislation_version_id == lc_alias.legislation_version_id,
            )
            .join(
                lct_alias,
                lc_alias.legislation_content_id == lct_alias.legislation_content_id,
            )
        )
        .where(Legislation.legislation_id.in_(legislation_ids))
    )
    results = await database.fetch_all(query)
    # Pivot it
    results_by_legislation_id = defaultdict(set)
    for result in results:
        results_by_legislation_id[result["legislation_id"]].update(result["tags"])
    return {
        legislation_id: normalize_tags(list(tags))
        for legislation_id, tags in results_by_legislation_id.items()
    }


async def get_bill_summaries(legislation_ids: List[int]) -> Dict[int, str]:
    """
    Get the LegislationContentSummary.summary for the legis-body Legislation.content_type for the highest LegislationContent.legislation_version_id for each legislation_id
    """
    database = await get_database()

    # Subquery to get the highest legislation_version_id for each legislation_id
    subquery = (
        select(
            LegislationVersion.legislation_id,
            func.max(LegislationVersion.legislation_version_id).label("max_version_id"),
        )
        .group_by(LegislationVersion.legislation_id)
        .subquery()
    )

    # Aliases for the tables
    lv_alias = aliased(LegislationVersion)
    lc_alias = aliased(LegislationContent)
    lcs_alias = aliased(LegislationContentSummary)
    # Main query to get distinct tags
    query = (
        select(Legislation.legislation_id, lcs_alias.summary)
        .select_from(
            join(
                Legislation,
                subquery,
                Legislation.legislation_id == subquery.c.legislation_id,
            )
            .join(
                lv_alias, lv_alias.legislation_version_id == subquery.c.max_version_id
            )
            .join(
                lc_alias,
                lv_alias.legislation_version_id == lc_alias.legislation_version_id,
            )
            .join(
                lcs_alias,
                lc_alias.legislation_content_id == lcs_alias.legislation_content_id,
            )
        )
        .where(Legislation.legislation_id.in_(legislation_ids))
    )
    results = await database.fetch_all(query)
    return {result["legislation_id"]: result["summary"] for result in results}


async def get_bill_appropriations(legislation_ids: List[int]) -> Dict[int, float]:
    """
    Get the Appropriation.amount for the legis-body Legislation.content_type for the highest LegislationContent.legislation_version_id for each legislation_id
    """
    database = await get_database()

    # Subquery to get the highest legislation_version_id for each legislation_id
    subquery = (
        select(
            LegislationVersion.legislation_id,
            func.max(LegislationVersion.legislation_version_id).label("max_version_id"),
        )
        .group_by(LegislationVersion.legislation_id)
        .subquery()
    )

    # Aliases for the tables
    lv_alias = aliased(LegislationVersion)
    lc_alias = aliased(LegislationContent)
    a_alias = aliased(Appropriation)
    # Main query to get distinct tags
    query = (
        select(Legislation.legislation_id, func.sum(a_alias.amount).label("amount"))
        .select_from(
            join(
                Legislation,
                subquery,
                Legislation.legislation_id == subquery.c.legislation_id,
            )
            .join(
                lv_alias, lv_alias.legislation_version_id == subquery.c.max_version_id
            )
            .join(
                lc_alias,
                lv_alias.legislation_version_id == lc_alias.legislation_version_id,
            )
            .join(
                a_alias,
                lc_alias.legislation_content_id == a_alias.legislation_content_id,
            )
        )
        .where(Legislation.legislation_id.in_(legislation_ids))
        .where(a_alias.parent_id == None)
        .group_by(Legislation.legislation_id)
    )
    results = await database.fetch_all(query)
    return {result["legislation_id"]: int(result["amount"]) for result in results}

async def get_bill_sponsor(legislation_ids: List[int]):
    database = await get_database()

    query = (
        select(
            *LegislatorMetadata.sqlalchemy_columns(),
            LegislationSponsorship.cosponsor,
            LegislationSponsorship.legislation_id,
        )
        .join(
            LegislationSponsorship,
            LegislationSponsorship.legislator_bioguide_id == Legislator.bioguide_id
        )
        .where(
            LegislationSponsorship.legislation_id.in_(legislation_ids),
            LegislationSponsorship.cosponsor == False
        )
        .group_by(
            LegislationSponsorship.legislation_id,
            Legislator.legislator_id,
            Legislator.bioguide_id,
            LegislationSponsorship.cosponsor
        )
        .order_by(LegislationSponsorship.cosponsor, Legislator.bioguide_id)
    )

    results = await database.fetch_all(query)
    return {result["legislation_id"]: dict(result) for result in results}

async def search_legislation(
    congress: str,
    chamber: str,
    versions: str,
    text: str,
    sort: str,
    page: int,
    page_size: int,
) -> Tuple[List[SearchResult], int]:
    database = await get_database()
    lv_alias = aliased(LegislationVersion)
    subquery = (
            select([1])
            .select_from(LegislationVersion)
            .where(
                (LegislationVersion.legislation_id == Legislation.legislation_id) &
                (LegislationVersion.legislation_version.in_(versions.upper().split(",")))
            )
        )
    legis_query = (
        select(
            Legislation.legislation_id,
            Legislation.title,
            Legislation.number,
            Congress.session_number,
            Legislation.legislation_type,
            Legislation.chamber,
            func.array_agg(lv_alias.legislation_version).label("versions"),
            func.array_agg(lv_alias.effective_date).label("effective_date"),
        )
        .select_from(
            join(
                Legislation,
                lv_alias,
                Legislation.legislation_id == lv_alias.legislation_id,
            ).join(Congress, Legislation.congress_id == Congress.congress_id)
        )
        .group_by(
            Legislation.legislation_id,
            Legislation.title,
            Congress.session_number,
            Legislation.number,
            Legislation.congress_id,
            Legislation.legislation_type,
            Legislation.chamber,
        )
        .having(exists(subquery))
        .order_by(sort, Legislation.legislation_id)
        .limit(page_size)
        .offset((page - 1) * page_size)
    )
    if congress:
        legis_query = legis_query.where(Congress.session_number == int(congress))
    if chamber:
        legis_query = legis_query.where(Legislation.chamber.in_(chamber.split(",")))

    if text:
        legis_query = legis_query.where(Legislation.title.ilike(f"%{text}%"))
    results = await database.fetch_all(legis_query)
    results = [dict(result) for result in results]

    legislation_ids = [result["legislation_id"] for result in results]

    tags_by_id = await get_distinct_tags(legislation_ids)
    summaries_by_id = await get_bill_summaries(legislation_ids)
    appropriations_by_id = await get_bill_appropriations(legislation_ids)
    sponsors_by_id = await get_bill_sponsor(legislation_ids)

    objs = [
        SearchResult(
            legislation_id=result["legislation_id"],
            legislation_type=result["legislation_type"],
            number=result["number"],
            title=result["title"],
            chamber=result["chamber"],
            congress=str(result["session_number"]),
            legislation_versions=[
                LegislationVersionEnum(x.upper()) for x in result["versions"]
            ],
            tags=sorted(tags_by_id.get(result["legislation_id"], [])),
            summary=summaries_by_id.get(result["legislation_id"], None),
            appropriations=appropriations_by_id.get(result["legislation_id"], None),
            sponsor=sponsors_by_id.get(result["legislation_id"], None),
            effective_date=result.get("effective_date")[0],
        )
        for result in results
    ]

    count_query = (
        select(
            func.count(Legislation.legislation_id),
        )
        .select_from(
            join(
                Legislation,
                lv_alias,
                Legislation.legislation_id == lv_alias.legislation_id,
            )
        )
        .group_by(
            Legislation.legislation_id,
        )
    ).having(exists(subquery))
    if congress:
        count_query = count_query.where(Congress.session_number == int(congress))
    if chamber:
        count_query = count_query.where(Legislation.chamber.in_(chamber.split(",")))

    if text:
        count_query = count_query.where(Legislation.title.ilike(f"%{text}%"))
    count_results = await database.fetch_all(count_query)
    return objs, len(count_results)
