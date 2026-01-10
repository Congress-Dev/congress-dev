from collections import defaultdict
from typing import Dict, List, Tuple

from sqlalchemy import select, join, func, distinct, exists
from sqlalchemy.orm import aliased
from congress_fastapi.db.postgres import get_database
from congress_db.models import (
    LegislativePolicyArea as LegislativePolicyAreaModel,
    LegislativePolicyAreaAssociation as LegislativePolicyAreaAssociationModel,
    LegislativeSubject as LegislativeSubjectModel,
    LegislativeSubjectAssociation as LegislativeSubjectAssociationModel,
)
from congress_fastapi.models.legislation.metadata import (
    LegislationPolicyArea,
    LegislationSubject,
)


async def get_legislation_policy_area(
    legislation_id: int,
) -> List[LegislationPolicyArea]:
    db = await get_database()
    query = (
        select(*LegislationPolicyArea.sqlalchemy_columns())
        .join(
            LegislativePolicyAreaAssociationModel,
            LegislativePolicyAreaAssociationModel.legislative_policy_area_id
            == LegislativePolicyAreaModel.legislative_policy_area_id,
        )
        .where(LegislativePolicyAreaAssociationModel.legislation_id == legislation_id)
    )
    results = await db.fetch_all(query)
    return [LegislationPolicyArea(**result) for result in results]


async def get_legislation_subjects(legislation_id: int) -> List[LegislationSubject]:
    db = await get_database()
    query = (
        select(*LegislationSubject.sqlalchemy_columns())
        .join(
            LegislativeSubjectAssociationModel,
            LegislativeSubjectAssociationModel.legislative_subject_id
            == LegislativeSubjectModel.legislative_subject_id,
        )
        .where(LegislativeSubjectAssociationModel.legislation_id == legislation_id)
    )
    results = await db.fetch_all(query)
    return [LegislationSubject(**result) for result in results]
