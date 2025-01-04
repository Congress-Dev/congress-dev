from typing import Dict, List

from congress_fastapi.models.legislation.content import LegislationContent
from congress_fastapi.handlers.legislation.actions import (
    get_legislation_version_actions_by_legislation_id,
)
from congress_fastapi.handlers.legislation.content import (
    get_legislation_content_by_legislation_version_id,
)
from congress_fastapi.models.legislation.actions import LegislationActionParse
from fastapi import APIRouter, HTTPException, Query, status

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


@router.get(
    "/legislation_version/{legislation_version_id}/actions",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": Error,
            "detail": "Legislation not found",
        },
        status.HTTP_200_OK: {
            "model": List[LegislationActionParse],
            "detail": "Actions for the clauses in the legislation",
        },
    },
)
async def get_legislation_version_actions(
    legislation_version_id: int,
) -> List[LegislationActionParse]:
    """Returns a list of LegislationActionParse objects for a given legislation_id"""
    obj = await get_legislation_version_actions_by_legislation_id(
        legislation_version_id
    )
    if obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Legislation not found"
        )
    return obj


@router.get(
    "/legislation_version/{legislation_version_id}/text",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": Error,
            "detail": "Legislation not found",
        },
        status.HTTP_200_OK: {
            "model": List[LegislationContent],
            "detail": "Text for the clauses in the legislation",
        },
    },
)
async def get_legislation_version_text(
    legislation_version_id: int,
    include_parsed: bool = Query(False, description="Include parsed actions"),
) -> List[LegislationContent]:
    """Returns a list of LegislationContent objects for a given legislation_id"""
    content_list = await get_legislation_content_by_legislation_version_id(
        legislation_version_id
    )
    if content_list is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Legislation not found"
        )

    if include_parsed:
        obj = await get_legislation_version_actions_by_legislation_id(
            legislation_version_id
        )
        action_by_content_id: Dict[int, List[LegislationActionParse]] = {}
        for action in obj:
            if action.legislation_content_id not in action_by_content_id:
                action_by_content_id[action.legislation_content_id] = []
            action_by_content_id[action.legislation_content_id].append(action)

        for content in content_list:
            if content.legislation_content_id in action_by_content_id:
                content.actions = action_by_content_id[content.legislation_content_id]
    return content_list
