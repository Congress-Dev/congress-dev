from typing import List
from billparser.db.models import LegislationVersionEnum

from billparser.prompt_runners.utils import (
    get_legis_by_parent_and_id,
    get_usc_content_by_parent_and_id,
    print_clause,
)
from congress_fastapi.handlers.legislation.content import (
    get_legislation_content_by_legislation_version_id,
)
from fastapi import APIRouter, HTTPException, Query, status

from congress_fastapi.handlers.legislation_metadata import (
    get_legislation_metadata_by_legislation_id,
    get_legislation_version_metadata_by_legislation_id,
)
from congress_fastapi.models.errors import Error
from congress_fastapi.models.legislation import LegislationMetadata

router = APIRouter(tags=["Legislation"])


@router.get(
    "/legislation/{legislation_id}/{version_str}",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": Error,
            "detail": "Legislation not found",
        },
        status.HTTP_200_OK: {
            "model": LegislationMetadata,
            "detail": "Basic info about the legislation",
        },
    },
)
async def get_legislation_by_id_and_version(
    legislation_id: int, version_str: LegislationVersionEnum
) -> LegislationMetadata:
    """Returns a LegislationMetadata object for a given legislation_id
    contains the data to render the legislation page"""
    obj = await get_legislation_metadata_by_legislation_id(legislation_id, version_str)
    if obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Legislation not found"
        )
    return obj


@router.get(
    "/legislation/{legislation_id}/latest/text",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": Error,
            "detail": "Legislation not found",
        },
        status.HTTP_200_OK: {
            "model": str,
            "detail": "Legislation text",
        },
    },
    tags=["MCP"],
)
async def get_legislation_by_id_and_version(legislation_id: int) -> str:
    """Returns the text for a legislation"""
    legis_versions = await get_legislation_version_metadata_by_legislation_id(
        legislation_id
    )
    legis_versions = sorted(
        legis_versions, key=lambda x: x.legislation_version_id, reverse=True
    )
    content = await get_legislation_content_by_legislation_version_id(
        legis_versions[0].legislation_version_id
    )
    content = sorted(content, key=lambda x: x.legislation_content_id)
    usc_by_parent, usc_by_id = get_legis_by_parent_and_id(content)
    return print_clause(usc_by_id, usc_by_parent, content[0].legislation_content_id)
