from collections import defaultdict
from typing import Dict, List, Tuple

from sqlalchemy import select, join, func, distinct, exists
from sqlalchemy.orm import aliased
from congress_fastapi.db.postgres import get_database
from congress_db.models import (
    LegislationActionParse as LegislationActionParseModel,
    LegislationAction as LegislationActionModel,
)
from congress_fastapi.models.legislation.actions import (
    LegislationActionParse,
    LegislationAction,
)


async def get_legislation_version_actions_by_legislation_id(
    legislation_version_id: int,
) -> List[LegislationActionParse]:
    db = await get_database()
    query = select(*LegislationActionParse.sqlalchemy_columns()).where(
        LegislationActionParseModel.legislation_version_id == legislation_version_id
    )
    results = await db.fetch_all(query)
    return [LegislationActionParse(**result) for result in results]


async def get_legislation_actions_by_legislation_id(
    legislation_id: int,
) -> List[LegislationAction]:
    db = await get_database()
    # For some reason the "same" action shows up with multiple sources
    # in the xml, but they have the same source_code, so just use that to filter
    # here.
    row_number = (
        func.row_number()
        .over(
            partition_by=LegislationActionModel.source_code,
            order_by=LegislationActionModel.action_date,
        )
        .label("rn")
    )
    subq = (
        select(*LegislationAction.sqlalchemy_columns(), row_number, LegislationActionModel.action_date.label("action_date"))
        .where(LegislationActionModel.legislation_id == legislation_id)
        .alias("legislation_subq")
    )
    query = (
        select(
            *[
                getattr(subq.c, col.key)
                for col in LegislationAction.sqlalchemy_columns()
            ]
        )
        .where(subq.c.rn == 1)
        .order_by(subq.c.action_date)
    )
    results = await db.fetch_all(query)
    return [LegislationAction(**result) for result in results]
