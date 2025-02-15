from typing import List, Optional, Tuple

from sqlalchemy import select, and_, or_, func, asc, desc

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
    congress: Optional[List[str]],
    chamber: Optional[List[str]],
    state: Optional[List[str]],
    *,
    sort: str,
    direction: str,
    page: int = 1,
    page_size: int = 10,
) -> Tuple[List[MemberSearchInfo], int]:
    database = await get_database()

    job_lookup = {
        'Senate': 'Senator',
        'House': 'Representative',
    }

    job = None
    if chamber is not None and chamber[0] != '':
        job = [job_lookup[x] for x in chamber]

    sessions = None
    if congress is not None and congress[0] != '':
        sessions = [int(c) for c in congress]

    sort_order = asc(sort)
    if direction == "desc":
        sort_order = desc(sort)

    query = select(*MemberSearchInfo.sqlalchemy_columns()).select_from(Legislator)
    if name:
        if ", " in name:
            name_parts = name.split(", ")
            print(name_parts)
            query = query.where(
                and_(
                    Legislator.first_name.ilike(f"%{name_parts[1]}%"),
                    Legislator.last_name.ilike(f"%{name_parts[0]}%"),
                )
            )
        elif " " in name:
            name_parts = name.split(" ")
            query = query.where(
                and_(
                    Legislator.first_name.ilike(f"%{name_parts[0]}%"),
                    Legislator.last_name.ilike(f"%{name_parts[1]}%"),
                )
            )
        else:
            query = query.where(
                or_(
                    Legislator.first_name.ilike(f"%{name}%"),
                    Legislator.last_name.ilike(f"%{name}%"),
                )
            )
    # if party:
    #     query = query.where(Legislator.party.in_(party))
    if sessions:
        query = query.where(
            or_(*[Legislator.congress_id.any(c) for c in sessions])
        )
    if job:
        query = query.where(Legislator.job.in_(job))
    # if state:
    #     query = query.where(Legislator.state.in_(state))
    query = query.order_by(sort_order, Legislator.last_name)
    query = query.limit(page_size)
    query = query.offset((page - 1) * page_size)
    result = await database.fetch_all(query)

    query = select(func.count(Legislator.legislator_id)).select_from(Legislator)
    if name:
        if ", " in name:
            name_parts = name.split(", ")
            print(name_parts)
            query = query.where(
                and_(
                    Legislator.first_name.ilike(f"%{name_parts[1]}%"),
                    Legislator.last_name.ilike(f"%{name_parts[0]}%"),
                )
            )
        elif " " in name:
            name_parts = name.split(" ")
            query = query.where(
                and_(
                    Legislator.first_name.ilike(f"%{name_parts[0]}%"),
                    Legislator.last_name.ilike(f"%{name_parts[1]}%"),
                )
            )
        else:
            query = query.where(
                or_(
                    Legislator.first_name.ilike(f"%{name}%"),
                    Legislator.last_name.ilike(f"%{name}%"),
                )
            )
    if sessions:
        query = query.where(
            or_(*[Legislator.congress_id.any(c) for c in sessions])
        )
    if job:
        query = query.where(Legislator.job.in_(job))
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
