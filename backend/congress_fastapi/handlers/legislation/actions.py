from collections import defaultdict
from typing import Dict, List, Tuple

from sqlalchemy import select, join, func, distinct, exists
from sqlalchemy.orm import aliased
from congress_fastapi.db.postgres import get_database
from billparser.db.models import (
    LegislationActionParse as LegislationActionParseModel,
)
from congress_fastapi.models.legislation.actions import LegislationActionParse


async def get_legislation_version_actions_by_legislation_id(
    legislation_version_id: int,
) -> List[LegislationActionParse]:
    db = await get_database()
    query = select(*LegislationActionParse.sqlalchemy_columns()).where(
        LegislationActionParseModel.legislation_version_id == legislation_version_id
    )
    results = await db.fetch_all(query)
    return [LegislationActionParse(**result) for result in results]
