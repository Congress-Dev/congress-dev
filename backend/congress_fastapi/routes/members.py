from typing import List

from fastapi import APIRouter, HTTPException, Query, status

from congress_fastapi.handlers.members import (
    get_member_by_bioguide_id,
    get_member_sponsorships_by_bioguide_id,
    get_members,
)
from congress_fastapi.models.errors import Error
from congress_fastapi.models.members import (
    LegislationSponsorshipList,
    MemberInfo,
    MemberSearchInfo,
    MemberSearchResponse,
)

router = APIRouter(tags=["Members"])


@router.get("/members")
async def get_members_search(
    page: int = Query(1, description="Offset for pagination"),
    page_size: int = Query(10, description="Number of members to return", alias="pageSize"),
    party: List[str] = Query(None, description="Filter by party"),
    congress: List[str] = Query(None, description="Filter by congress"),
    chamber: List[str] = Query(None, description="Filter by chamber"),
    state: List[str] = Query(None, description="Filter by state"),
    name: str = Query(None, description="Filter by name"),
    sort: str = Query(None),
    direction: str = Query("asc"),
    responses={
        status.HTTP_200_OK: {
            "model": MemberSearchResponse,
            "detail": "List of members",
        },
    },
) -> MemberSearchResponse:
    """
    Returns a list of MemberInfo objects based on the provided search criteria.

    - **pageSize**: Number of members to return. Default is 10.
    - **page**: Offset for pagination. Default is 1.
    - **party**: Filter by party. Default is None.
    - **chamber**: Filter by chamber. Default is None.
    - **state**: Filter by state. Default is None.
    - **name**: Filter by name. Default is None.

    Returns:
        `List[MemberSearchInfo]`: List of members matching the search criteria.
    """
    member_list, total_results = await get_members(
        name, party, congress, chamber, state, sort=sort, direction=direction, page=page, page_size=page_size
    )
    result = {
        "members": member_list,
        "total_results": total_results,
    }
    return result


@router.get(
    "/member/{bioguide_id}",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": Error,
            "detail": "Member not found",
        },
        status.HTTP_200_OK: {
            "model": MemberInfo,
            "detail": "Basic info about the member",
        },
    },
)
async def get_member_info(bioguide_id: str) -> MemberInfo:
    """Returns a MemberInfo object for a given bioguide_id"""
    obj = await get_member_by_bioguide_id(bioguide_id)
    if obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Member not found"
        )
    return obj


@router.get("/member/{bioguide_id}/sponsorships")
async def get_member_sponsorships(
    bioguide_id: str,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": Error,
            "detail": "Member not found",
        },
        status.HTTP_200_OK: {
            "model": LegislationSponsorshipList,
            "detail": "Basic info about the member",
        },
    },
) -> LegislationSponsorshipList:
    """Returns a list of LegislationSponsorshipInfo objects for a given bioguide_id"""
    obj = await get_member_by_bioguide_id(bioguide_id)
    if obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Member not found"
        )
    sponsorships = await get_member_sponsorships_by_bioguide_id(bioguide_id)
    return LegislationSponsorshipList(legislation_sponsorships=sponsorships)
