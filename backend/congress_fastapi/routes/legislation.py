from typing import List

from fastapi import APIRouter, HTTPException, Query, status

from congress_fastapi.handlers.legislation_metadata import (
    get_legislation_metadata_by_legislation_id,
)
from congress_fastapi.models.errors import Error
from congress_fastapi.models.legislation import LegislationMetadata

router = APIRouter()


@router.get(
    "/legislation/{legislation_id}",
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
async def get_legislation_by_id(legislation_id: int) -> LegislationMetadata:
    """Returns a LegislationMetadata object for a given legislation_id
    contains the data to render the legislation page"""
    obj = await get_legislation_metadata_by_legislation_id(legislation_id)
    if obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Legislation not found"
        )
    return obj
