from typing import List
from billparser.db.models import LegislationChamber, LegislationVersionEnum

from fastapi import APIRouter, HTTPException, Query, status

from congress_fastapi.handlers.legislation.search import (
    search_legislation,
)
from congress_fastapi.models.errors import Error
from congress_fastapi.models.legislation.search import SearchResponse, SearchResult

router = APIRouter()


@router.get(
    "/legislation/search",
)
async def get_search_legislation(
    query: str = Query(None),
    congress: str = Query(None),
    chamber: str = Query(None),
    versions: str = Query(None),
    results: int = Query(10),
    sort: str = Query(None),
    page: int = Query(1),
    page_size: int = Query(10, alias="pageSize"),
) -> SearchResponse:
    """Returns a list of LegislationMetadata objects for a given query"""
    obj, total = await search_legislation(
        congress, chamber, versions, query, sort, page, page_size
    )
    if obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Legislation not found"
        )
    return SearchResponse(legislation=obj, total_results=total)
