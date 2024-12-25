from typing import List

from fastapi import APIRouter, HTTPException, status

from congress_fastapi.handlers.legislation_version import (
    get_legislation_version_tags_by_legislation_id,
    get_legislation_version_summaries_by_legislation_id,
)
from congress_fastapi.models.errors import Error
from congress_fastapi.models.legislation import (
    LegislationClauseTag,
    LegislationClauseSummary,
)

router = APIRouter()


@router.get(
    "/legislation_version/{legislation_version_id}/tags",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": Error,
            "detail": "Legislation not found",
        },
        status.HTTP_200_OK: {
            "model": List[LegislationClauseTag],
            "detail": "Tags for the clauses in the legislation",
        },
    },
)
async def get_legislation_version_tags(
    legislation_version_id: int,
) -> List[LegislationClauseTag]:
    """Returns a list of LegislationClauseTag objects for a given legislation_id"""
    obj = await get_legislation_version_tags_by_legislation_id(legislation_version_id)
    if obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Legislation not found"
        )
    return obj


@router.get(
    "/legislation_version/{legislation_version_id}/summaries",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": Error,
            "detail": "Legislation not found",
        },
        status.HTTP_200_OK: {
            "model": List[LegislationClauseTag],
            "detail": "Summaries for the sections in the legislation",
        },
    },
)
async def get_legislation_version_summaries(
    legislation_version_id: int,
) -> List[LegislationClauseSummary]:
    """Returns a list of LegislationClauseSummary objects for a given legislation_id"""
    obj = await get_legislation_version_summaries_by_legislation_id(
        legislation_version_id
    )
    if obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Legislation not found"
        )
    return obj
