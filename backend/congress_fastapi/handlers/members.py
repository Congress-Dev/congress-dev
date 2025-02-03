from typing import List, Optional, Tuple

from sqlalchemy import select, and_, or_, func

from billparser.db.models import (
    Legislation,
    LegislationSponsorship,
    Legislator,
    LegislationVersion,
    Congress,
)
from congress_fastapi.db.postgres import get_database
from congress_fastapi.models.members import (
    LegislationSponsorshipInfo,
    MemberInfo,
    MemberSearchInfo,
)


async def get_members(
    name: Optional[str],
    party: Optional[List[str]],
    chamber: Optional[str],
    state: Optional[List[str]],
    *,
    limit: int = 10,
    offset: int = 0,
) -> Tuple[List[MemberSearchInfo], int]:
    database = await get_database()
    query = select(*MemberSearchInfo.sqlalchemy_columns()).select_from(Legislator)
    if name:
        query = query.where(
            or_(
                Legislator.first_name.ilike(f"%{name}%"),
                Legislator.last_name.ilike(f"%{name}%"),
            )
        )
    # if party:
    #     query = query.where(Legislator.party.in_(party))
    # if chamber:
    #     query = query.where(Legislator.chamber == chamber)
    # if state:
    #     query = query.where(Legislator.state.in_(state))
    query = query.limit(limit).offset(offset)
    result = await database.fetch_all(query)
    if result is None:
        return None
    if len(result) == 0:
        return []
    query = select(func.count(Legislator.legislator_id)).select_from(Legislator)
    if name:
        query = query.where(
            or_(
                Legislator.first_name.ilike(f"%{name}%"),
                Legislator.last_name.ilike(f"%{name}%"),
            )
        )
    query = query.limit(limit).offset(offset)
    count_result = await database.fetch_one(query)
    return [MemberSearchInfo(**r) for r in result], count_result[0]


async def get_member_by_bioguide_id(bioguide_id: str) -> MemberInfo:
    """
    Returns a MemberInfo object for a given bioguide_id
    """
    database = await get_database()
    query = select(*MemberInfo.sqlalchemy_columns()).where(
        Legislator.bioguide_id == bioguide_id
    )
    result = await database.fetch_one(query)
    if result is None:
        return None
    return MemberInfo(**result)


async def get_member_sponsorships_by_bioguide_id(
    bioguide_id: str,
) -> List[LegislationSponsorshipInfo]:
    """
    Returns a list of LegislationSponsorshipInfo objects for a given bioguide_id
    """
    database = await get_database()

    query = (
        select(
            *LegislationSponsorshipInfo.sqlalchemy_columns(),
        )
        .select_from(LegislationSponsorship)
        .join(
            Legislation,
            Legislation.legislation_id == LegislationSponsorship.legislation_id,
        )
        .join(Congress, Legislation.congress_id == Congress.congress_id)
        .join(
            Legislator,
            Legislator.bioguide_id == LegislationSponsorship.legislator_bioguide_id,
        )
        .where(LegislationSponsorship.legislator_bioguide_id == bioguide_id)
        .where(LegislationSponsorship.cosponsor == False)
    )

    result = await database.fetch_all(query)
    if result is None:
        return None
    if len(result) == 0:
        return []
    return [LegislationSponsorshipInfo(**r) for r in result]
