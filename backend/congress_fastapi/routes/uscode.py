from typing import Any, Dict, List
from billparser.db.models import LegislationVersionEnum

from congress_fastapi.handlers.uscode import search_chroma
from congress_fastapi.models.uscode import USCodeSearchRequest, USCodeSearchResponse
from fastapi import APIRouter, HTTPException, Query, status

from congress_fastapi.handlers.legislation_metadata import (
    get_legislation_metadata_by_legislation_id,
)
from congress_fastapi.models.errors import Error
from congress_fastapi.models.legislation import LegislationMetadata

router = APIRouter(tags=["USCode"])

@router.post("/uscode/search")
async def post_uscode_search(body: USCodeSearchRequest) -> List[USCodeSearchResponse]:
    return await search_chroma(body.query, body.results)