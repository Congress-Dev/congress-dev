from typing import List
from congress_db.models import LegislationChamber, LegislationVersionEnum

from fastapi import APIRouter, HTTPException, Query, status

from congress_fastapi.handlers.legislation.search import (
    search_legislation,
    get_legislation_tag_options,
)
from congress_fastapi.models.errors import Error
from congress_fastapi.models.legislation.search import SearchResponse, SearchResult

router = APIRouter(tags=["Legislation"])


@router.get(
    "/legislation/search-tags",
)
async def get_search_tags() -> List[str]:
    """Returns a list of tags for all legislation"""
    return await get_legislation_tag_options()


@router.get("/legislation/search", tags=["MCP"])
async def get_search_legislation(
    text: str = Query(None),
    congress: str = Query(None),
    chamber: str = Query(None),
    versions: str = Query(None),
    sort: str = Query(None),
    direction: str = Query("asc"),
    page: int = Query(1),
    tags: str = Query(None),
    page_size: int = Query(10, alias="pageSize"),
) -> SearchResponse:
    """Returns a list of LegislationMetadata objects for a given query"""
    obj, total = await search_legislation(
        congress, chamber, versions, text, tags, sort, direction, page, page_size
    )
    if obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Legislation not found"
        )
    return SearchResponse(legislation=obj, total_results=total)
