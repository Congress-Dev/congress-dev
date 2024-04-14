from typing import List

from fastapi import APIRouter, HTTPException, Query, status

from congress_fastapi.handlers.members import (
    get_member_by_bioguide_id,
    get_member_sponsorships_by_bioguide_id,
)
from congress_fastapi.models.errors import Error
from congress_fastapi.models.members import LegislationSponsorshipList, MemberInfo

router = APIRouter()


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
    cosponsored: bool = Query(
        True, description="Should cosponsored bills be included?"
    ),
    sponsored: bool = Query(True, description="Should sponsored bills be included?"),
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
    print("Got req")
    obj = await get_member_by_bioguide_id(bioguide_id)
    if obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Member not found"
        )
    sponsorships = await get_member_sponsorships_by_bioguide_id(
        bioguide_id, sponsored, cosponsored
    )
    return LegislationSponsorshipList(legislation_sponsorships=sponsorships)
