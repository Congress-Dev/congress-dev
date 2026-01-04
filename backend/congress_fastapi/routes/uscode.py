from typing import Any, Dict, List
from congress_db.models import LegislationVersionEnum

from congress_fastapi.handlers.uscode import read_usc_content, search_chroma
from congress_fastapi.models.uscode import USCodeSearchRequest, USCodeSearchResponse
from fastapi import APIRouter, HTTPException, Query, status

from congress_fastapi.handlers.legislation_metadata import (
    get_legislation_metadata_by_legislation_id,
)
from congress_fastapi.models.errors import Error
from congress_fastapi.models.legislation import LegislationMetadata
from congress_parser.prompt_runners.utils import (
    get_usc_content_by_parent_and_id,
    print_clause,
)


router = APIRouter(tags=["USCode"])


@router.post("/uscode/search", tags=["MCP"])
async def post_uscode_search(body: USCodeSearchRequest) -> List[USCodeSearchResponse]:
    return await search_chroma(body.query, body.results)


@router.get("/uscode/{title}/{section}", tags=["MCP"])
async def get_uscode_section(
    title: str,
    section: str,
) -> str:
    # Get the legislation metadata
    citation = f"/us/usc/t{title}/s{section}"
    section_obj = await read_usc_content(4, citation)
    section_children = await read_usc_content(4, citation + "/%")
    combined = section_obj + section_children
    if not combined:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="US Code section not found",
        )
    usc_by_parent, usc_by_id = get_usc_content_by_parent_and_id(combined)
    return print_clause(usc_by_id, usc_by_parent, section[0].usc_content_id)
