from typing import Dict, List

from billparser.db.models import User
from billparser.prompt_runners.utils import get_legis_by_parent_and_id, print_clause
from congress_fastapi.models.legislation.content import LegislationContent
from congress_fastapi.handlers.legislation.actions import (
    get_legislation_version_actions_by_legislation_id,
)
from congress_fastapi.handlers.legislation.content import (
    get_legislation_content_by_legislation_version_id,
)
from congress_fastapi.handlers.legislation_metadata import (
    get_legislation_metadata_by_version_id,
)
from congress_fastapi.models.legislation.actions import LegislationActionParse
from congress_fastapi.models.legislation.llm import LLMRequest
from congress_fastapi.routes.user import user_from_cookie
from congress_fastapi.utils.limiter import limiter
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from congress_fastapi.handlers.legislation_version import (
    get_legislation_version_tags_by_legislation_id,
    get_legislation_version_summaries_by_legislation_id,
    run_talk_to_bill_prompt,
)
from congress_fastapi.models.errors import Error
from congress_fastapi.models.legislation import (
    LegislationClauseTag,
    LegislationClauseSummary,
)

router = APIRouter(tags=["Legislation", "Legislation Version"])


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


@router.post(
    "/legislation_version/{legislation_version_id}/llm",
)
@limiter.limit("5/5minutes")
async def post_legislation_version_llm(
    legislation_version_id: int,
    query_request: LLMRequest,
    request: Request,
    user: User = Depends(user_from_cookie),
) -> None:
    """Returns a list of LegislationContent objects for a given legislation_id"""
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not logged in"
        )
    legis_content = await get_legislation_content_by_legislation_version_id(
        legislation_version_id
    )
    legis_by_parent, legis_by_id = get_legis_by_parent_and_id(legis_content)
    legis_body = legis_by_parent[None][0]
    content = print_clause(
        legis_by_id, legis_by_parent, legis_body.legislation_content_id
    )

    metadata = await get_legislation_metadata_by_version_id(legislation_version_id)
    metadata_context = """== Sponsor ==
{sponsor}
== Cosponsors ==
{cosponsors}
    """.format(
        sponsor=f"{metadata.sponsor.first_name} {metadata.sponsor.last_name}",
        cosponsors=",".join(
            [
                f"{cosponsor.first_name} {cosponsor.last_name}"
                for cosponsor in metadata.cosponsors
            ]
        ),
    )
    return await run_talk_to_bill_prompt(query_request.query, content, metadata_context)
