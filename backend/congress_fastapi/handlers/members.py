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
