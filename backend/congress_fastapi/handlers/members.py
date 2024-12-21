from typing import List

from sqlalchemy import select, and_

from billparser.db.models import (
    Legislation,
    LegislationSponsorship,
    Legislator,
    LegislationVersion,
    Congress,
)
from congress_fastapi.db.postgres import get_database
from congress_fastapi.models.members import LegislationSponsorshipInfo, MemberInfo


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
    sponsored: bool = True,
    cosponsored: bool = True,
) -> List[LegislationSponsorshipInfo]:
    """
    Returns a list of LegislationSponsorshipInfo objects for a given bioguide_id
    """
    database = await get_database()
    print(*LegislationSponsorshipInfo.sqlalchemy_columns())
    most_recent_version = (
        select(LegislationVersion.legislation_id)
        .order_by(LegislationVersion.created_at.desc())
        .limit(1)
    )
    query = (
        select(
            *LegislationSponsorshipInfo.sqlalchemy_columns(),
        )
        .join(Congress, Legislation.congress_id == Congress.congress_id)
        .join(
            LegislationSponsorship,
            Legislation.legislation_id == LegislationSponsorship.legislation_id,
        )
        .join(
            LegislationVersion,
            and_(
                Legislation.legislation_id == LegislationVersion.legislation_id,
                LegislationVersion.legislation_id.in_(most_recent_version),
            ),
        )
        .where(LegislationSponsorship.legislator_bioguide_id == bioguide_id)
    )
    conds = []
    if sponsored:
        conds.append(LegislationSponsorship.cosponsor.is_(False))
    if cosponsored:
        conds.append(LegislationSponsorship.cosponsor.is_(True))
    # If we have both, we don't need to filter
    if len(conds) == 1:
        query = query.where(conds[0])
    print(query)
    result = await database.fetch_all(query)
    if result is None:
        return None
    if len(result) == 0:
        return []
    return [LegislationSponsorshipInfo(**r) for r in result]
