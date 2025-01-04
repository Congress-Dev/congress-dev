from collections import defaultdict
from typing import Dict, List, Tuple

from sqlalchemy import select, join, func, distinct, exists
from sqlalchemy.orm import aliased
from congress_fastapi.db.postgres import get_database
from billparser.db.models import (
    LegislationContent as LegislationContentModel,
)
from congress_fastapi.models.legislation.content import LegislationContent


async def get_legislation_content_by_legislation_version_id(
    legislation_version_id: int,
) -> List[LegislationContent]:
    db = await get_database()
    query = select(*LegislationContent.sqlalchemy_columns()).where(
        LegislationContentModel.legislation_version_id == legislation_version_id
    )
    results = await db.fetch_all(query)
    print(results)
    return [LegislationContent(**result) for result in results]
