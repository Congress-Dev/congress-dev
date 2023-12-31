from congress_fastapi.db.postgres import get_database
from sqlalchemy import select

from billparser.db.models import Legislator
from congress_fastapi.models.members import MemberInfo


async def get_member_by_bioguide_id(bioguide_id: str) -> MemberInfo:
    """
    Returns a MemberInfo object for a given bioguide_id
    """
    database = await get_database()
    query = select(*MemberInfo.sqlalchemy_columns()).where(
        Legislator.bioguide_id == bioguide_id
    )
    results = await database.fetch_one(query)
    return MemberInfo(**results)
