from typing import List

from sqlalchemy import select

from congress_fastapi.db.postgres import get_database
from billparser.db.models import LegislationContentTag, LegislationContent

from congress_fastapi.models.legislation import LegislationClauseTag


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
