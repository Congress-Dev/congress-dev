from typing import List, Optional, Tuple

from sqlalchemy import select, and_, or_, func, asc, desc, insert, update, delete
from sqlalchemy.orm import aliased

from billparser.db.models import (
    LegislationCommittee,
    LegislationChamber,
    Congress,
)
from congress_fastapi.db.postgres import get_database
from congress_fastapi.models.committees import (
    LegislationCommitteeInfo,
)


async def get_committees(
    name: Optional[str] = None,
    chamber: Optional[List[str]] = None,
    congress: Optional[List[str]] = None,
    committee_type: Optional[str] = None,
    *,
    sort: str = "name",
    direction: str = "asc",
    page: int = 1,
    page_size: int = 10,
) -> Tuple[List[LegislationCommitteeInfo], int]:
    """
    Get committees with optional filtering and pagination
    """
    database = await get_database()

    # Build sort order
    sort_column = getattr(LegislationCommittee, sort, LegislationCommittee.name)
    sort_order = asc(sort_column) if direction == "asc" else desc(sort_column)

    # Build base query
    query = select(*LegislationCommitteeInfo.sqlalchemy_columns()).select_from(
        LegislationCommittee
    )

    # Apply filters
    if name:
        query = query.where(LegislationCommittee.name.ilike(f"%{name}%"))

    if chamber:
        chamber_enums = [LegislationChamber.from_string(c) for c in chamber if c]
        if chamber_enums:
            query = query.where(LegislationCommittee.chamber.in_(chamber_enums))

    if congress:
        congress_numbers = [int(c) for c in congress if c.isdigit()]
        if congress_numbers:
            query = query.join(Congress).where(Congress.session_number.in_(congress_numbers))

    if committee_type:
        query = query.where(
            LegislationCommittee.committee_type.ilike(f"%{committee_type}%")
        )

    # Apply sorting and pagination
    query = query.order_by(sort_order)
    query = query.limit(page_size)
    query = query.offset((page - 1) * page_size)

    result = await database.fetch_all(query)

    # Get parent names for committees that have parent_id
    committee_results = [dict(r) for r in result]
    parent_ids = [r["parentId"] for r in committee_results if r.get("parentId") is not None]
    
    parent_names = {}
    if parent_ids:
        parent_query = select(
            LegislationCommittee.legislation_committee_id,
            LegislationCommittee.name
        ).where(LegislationCommittee.legislation_committee_id.in_(parent_ids))
        
        parent_result = await database.fetch_all(parent_query)
        parent_names = {r["legislation_committee_id"]: r["name"] for r in parent_result}

    # Add parent names to results
    for committee in committee_results:
        committee["parent_name"] = parent_names.get(committee.get("parentId"))

    # Get total count
    count_query = select(
        func.count(LegislationCommittee.legislation_committee_id)
    ).select_from(LegislationCommittee)

    # Apply same filters to count query
    if name:
        count_query = count_query.where(LegislationCommittee.name.ilike(f"%{name}%"))

    if chamber:
        chamber_enums = [LegislationChamber.from_string(c) for c in chamber if c]
        if chamber_enums:
            count_query = count_query.where(
                LegislationCommittee.chamber.in_(chamber_enums)
            )

    if congress:
        congress_ids = [int(c) for c in congress if c.isdigit()]
        if congress_ids:
            count_query = count_query.where(
                LegislationCommittee.congress_id.in_(congress_ids)
            )

    if committee_type:
        count_query = count_query.where(
            LegislationCommittee.committee_type.ilike(f"%{committee_type}%")
        )

    count_result = await database.fetch_one(count_query)

    return [LegislationCommitteeInfo(**r) for r in committee_results], count_result[0]


async def get_committee_by_id(committee_id: int) -> Optional[LegislationCommitteeInfo]:
    """
    Get a committee by its ID
    """
    database = await get_database()
    query = select(*LegislationCommitteeInfo.sqlalchemy_columns()).where(
        LegislationCommittee.legislation_committee_id == committee_id
    )
    result = await database.fetch_one(query)
    if result is None:
        return None
    return LegislationCommitteeInfo(**result)


async def get_committees_by_congress(
    congress_id: int,
) -> List[LegislationCommitteeInfo]:
    """
    Get all committees for a specific congress
    """
    database = await get_database()

    query = (
        select(*LegislationCommitteeInfo.sqlalchemy_columns())
        .select_from(LegislationCommittee)
        .where(LegislationCommittee.congress_id == congress_id)
        .order_by(LegislationCommittee.name)
    )

    result = await database.fetch_all(query)
    return [LegislationCommitteeInfo(**r) for r in result]


async def get_subcommittees(parent_committee_id: int) -> List[LegislationCommitteeInfo]:
    """
    Get all subcommittees for a parent committee
    """
    database = await get_database()

    query = (
        select(*LegislationCommitteeInfo.sqlalchemy_columns())
        .select_from(LegislationCommittee)
        .where(LegislationCommittee.parent_id == parent_committee_id)
        .order_by(LegislationCommittee.name)
    )

    result = await database.fetch_all(query)
    return [LegislationCommitteeInfo(**r) for r in result]
