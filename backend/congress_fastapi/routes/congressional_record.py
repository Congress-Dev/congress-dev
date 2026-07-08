from typing import List, Optional
from datetime import date

from fastapi import APIRouter, HTTPException, Query, status

from congress_fastapi.handlers.congressional_record import (
    get_issues,
    get_issue_detail,
    get_granule_detail,
    get_speaker_stats,
    get_activity_calendar,
)
from congress_fastapi.models.congressional_record import (
    CRECIssueListResponse,
    CRECIssueDetailResponse,
    CRECGranuleDetailResponse,
    CRECSpeakerStatsResponse,
    CRECActivityResponse,
)
from congress_fastapi.models.errors import Error

router = APIRouter(tags=["Congressional Record"])


@router.get("/congressional-record")
async def list_issues(
    page: int = Query(1, description="Page number"),
    page_size: int = Query(20, alias="pageSize"),
    start_date: Optional[date] = Query(None, alias="startDate"),
    end_date: Optional[date] = Query(None, alias="endDate"),
    chamber: Optional[str] = Query(None, description="Filter by chamber section"),
) -> CRECIssueListResponse:
    """List Congressional Record daily issues with pagination and date filtering."""
    issues, total = await get_issues(start_date, end_date, chamber, page, page_size)
    return CRECIssueListResponse(issues=issues, total_results=total)


@router.get(
    "/congressional-record/{issue_id}",
    responses={
        status.HTTP_404_NOT_FOUND: {"model": Error, "detail": "Issue not found"},
    },
)
async def get_issue(issue_id: int) -> CRECIssueDetailResponse:
    """Get a single Congressional Record issue with its granules."""
    issue, granules = await get_issue_detail(issue_id)
    if issue is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found"
        )
    return CRECIssueDetailResponse(issue=issue, granules=granules)


@router.get(
    "/congressional-record/{issue_id}/granule/{granule_id}",
    responses={
        status.HTTP_404_NOT_FOUND: {"model": Error, "detail": "Granule not found"},
    },
)
async def get_granule(issue_id: int, granule_id: int) -> CRECGranuleDetailResponse:
    """Get a granule with all its speeches and bill references."""
    granule, speeches, summary = await get_granule_detail(granule_id)
    if granule is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Granule not found"
        )
    return CRECGranuleDetailResponse(
        granule=granule, speeches=speeches, summary=summary
    )


@router.get("/congressional-record/stats/speakers")
async def speaker_statistics(
    start_date: Optional[date] = Query(None, alias="startDate"),
    end_date: Optional[date] = Query(None, alias="endDate"),
    chamber: Optional[str] = Query(None),
    limit: int = Query(20),
    page: int = Query(1),
) -> CRECSpeakerStatsResponse:
    """Get speaker statistics - who talked the most by word count."""
    speakers, total = await get_speaker_stats(
        start_date, end_date, chamber, limit, page
    )
    return CRECSpeakerStatsResponse(speakers=speakers, total_results=total)


@router.get("/congressional-record/stats/activity")
async def activity_calendar(
    start_date: Optional[date] = Query(None, alias="startDate"),
    end_date: Optional[date] = Query(None, alias="endDate"),
) -> CRECActivityResponse:
    """Get activity calendar data for heatmap visualization."""
    activity = await get_activity_calendar(start_date, end_date)
    return CRECActivityResponse(activity=activity)
