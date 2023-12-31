from fastapi import APIRouter, HTTPException, status

from congress_fastapi.models.errors import Error
from congress_fastapi.models.members import MemberInfo
from congress_fastapi.handlers.members import get_member_by_bioguide_id

router = APIRouter()


@router.get(
    "/members/{bioGuideId}",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": Error,
            "detail": "Member not found",
        },
        status.HTTP_200_OK: {
            "model": MemberInfo,
            "detail": "Basic info about the member",
        }
    },
)
async def get_member_info(bioGuideId: str) -> MemberInfo:
    """Returns a MemberInfo object for a given bioguide_id"""
    obj = await get_member_by_bioguide_id(bioGuideId)
    if obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Member not found"
        )
    return obj
