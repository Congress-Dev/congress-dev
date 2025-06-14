from typing import List

from fastapi import APIRouter, HTTPException, Query, status

from congress_fastapi.handlers.committees import (
    get_committees,
    get_committee_by_id,
    get_committees_by_congress,
    get_subcommittees,
)
from congress_fastapi.models.errors import Error
from congress_fastapi.models.committees import (
    LegislationCommitteeInfo,
    LegislationCommitteeSearchResponse,
)

router = APIRouter(tags=["Committees"])


@router.get("/committees")
async def get_committees_search(
    page: int = Query(1, description="Offset for pagination"),
    page_size: int = Query(
        10, description="Number of committees to return", alias="pageSize"
    ),
    name: str = Query(None, description="Filter by committee name"),
    chamber: List[str] = Query(None, description="Filter by chamber"),
    congress: List[str] = Query(None, description="Filter by congress"),
    committee_type: str = Query(None, description="Filter by committee type"),
    sort: str = Query("name", description="Sort field"),
    direction: str = Query("asc", description="Sort direction"),
) -> LegislationCommitteeSearchResponse:
    """
    Returns a list of LegislationCommitteeInfo objects based on the provided search criteria.

    - **pageSize**: Number of committees to return. Default is 10.
    - **page**: Offset for pagination. Default is 1.
    - **name**: Filter by committee name. Default is None.
    - **chamber**: Filter by chamber. Default is None.
    - **congress**: Filter by congress. Default is None.
    - **committee_type**: Filter by committee type. Default is None.
    - **sort**: Sort field. Default is "name".
    - **direction**: Sort direction. Default is "asc".

    Returns:
        `LegislationCommitteeSearchResponse`: List of committees matching the search criteria.
    """
    committee_list, total_results = await get_committees(
        name=name,
        chamber=chamber,
        congress=congress,
        committee_type=committee_type,
        sort=sort,
        direction=direction,
        page=page,
        page_size=page_size,
    )

    return LegislationCommitteeSearchResponse(
        committees=committee_list, total_results=total_results
    )


@router.get(
    "/committee/{committee_id}",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": Error,
            "detail": "Committee not found",
        },
        status.HTTP_200_OK: {
            "model": LegislationCommitteeInfo,
            "detail": "Basic info about the committee",
        },
    },
)
async def get_committee_info(committee_id: int) -> LegislationCommitteeInfo:
    """Returns a LegislationCommitteeInfo object for a given committee_id"""
    obj = await get_committee_by_id(committee_id)
    if obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Committee not found"
        )
    return obj


@router.get(
    "/congress/{congress_id}/committees",
    responses={
        status.HTTP_200_OK: {
            "model": List[LegislationCommitteeInfo],
            "detail": "List of committees for the congress",
        },
    },
)
async def get_committees_by_congress_endpoint(
    congress_id: int,
) -> List[LegislationCommitteeInfo]:
    """Returns all committees for a specific congress"""
    return await get_committees_by_congress(congress_id)


@router.get(
    "/committee/{committee_id}/subcommittees",
    responses={
        status.HTTP_200_OK: {
            "model": List[LegislationCommitteeInfo],
            "detail": "List of subcommittees for the parent committee",
        },
    },
)
async def get_subcommittees_endpoint(
    committee_id: int,
) -> List[LegislationCommitteeInfo]:
    """Returns all subcommittees for a parent committee"""
    return await get_subcommittees(committee_id)
