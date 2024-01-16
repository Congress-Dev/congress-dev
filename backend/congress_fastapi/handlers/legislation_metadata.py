from typing import List, Optional

from sqlalchemy import or_, select, func, and_

from billparser.db.models import (
    Legislation,
    LegislationVersion,
)
from congress_fastapi.db.postgres import get_database
from congress_fastapi.models.legislation import (
    LegislationMetadata,
    LegislationVersionMetadata,
)


async def get_legislation_version_metadata_by_legislation_id(
    legislation_id: int,
) -> Optional[List[LegislationVersionMetadata]]:
    """
    Returns a list of LegislationVersionMetadata objects for a given legislation_id
    """
    database = await get_database()
    query = (
        select(
            *LegislationVersionMetadata.sqlalchemy_columns(),
        )
        .where(LegislationVersion.legislation_id == legislation_id)
        .order_by(LegislationVersion.effective_date)
    )
    results = await database.fetch_all(query)
    if results is None:
        return None
    return [LegislationVersionMetadata(**result) for result in results]


async def get_legislation_metadata_by_legislation_id(
    legislation_id: int,
) -> Optional[LegislationMetadata]:
    """
    Returns a LegislationMetadata object for a given legislation_id
    """
    database = await get_database()
    query = select(
        *LegislationMetadata.sqlalchemy_columns(),
    ).where(Legislation.legislation_id == legislation_id)
    result = await database.fetch_one(query)
    if result is None:
        return None
    legis_versions = await get_legislation_version_metadata_by_legislation_id(
        legislation_id
    )

    usc_release_id = legis_versions[0].usc_release_id
    return LegislationMetadata(
        legislation_versions=legis_versions, usc_release_id=usc_release_id, **result
    )
