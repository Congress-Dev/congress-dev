from typing import Annotated, List, Optional
from datetime import date, datetime

from pydantic import BaseModel
from congress_fastapi.models.abstract import MappableBase
from congress_db.models import (
    CRECIssue,
    CRECGranule,
    CRECSpeech,
    CRECBillReference,
)


class CRECIssueInfo(MappableBase):
    crec_issue_id: Annotated[int, CRECIssue.crec_issue_id]
    issue_date: Annotated[Optional[date], CRECIssue.issue_date]
    congress_id: Annotated[Optional[int], CRECIssue.congress_id]
    package_id: Annotated[Optional[str], CRECIssue.package_id]


class CRECIssueListResponse(BaseModel):
    issues: List[CRECIssueInfo]
    total_results: int


class CRECGranuleInfo(MappableBase):
    crec_granule_id: Annotated[int, CRECGranule.crec_granule_id]
    crec_issue_id: Annotated[Optional[int], CRECGranule.crec_issue_id]
    granule_id: Annotated[Optional[str], CRECGranule.granule_id]
    section: Annotated[Optional[str], CRECGranule.section]
    title: Annotated[Optional[str], CRECGranule.title]
    page_start: Annotated[Optional[str], CRECGranule.page_start]
    page_end: Annotated[Optional[str], CRECGranule.page_end]
    order_number: Annotated[Optional[int], CRECGranule.order_number]


class CRECIssueDetailResponse(BaseModel):
    issue: CRECIssueInfo
    granules: List[CRECGranuleInfo]


class CRECSpeechInfo(BaseModel):
    crec_speech_id: int
    speaker_raw: Optional[str] = None
    legislator_bioguide_id: Optional[str] = None
    order_number: Optional[int] = None
    content_text: Optional[str] = None
    word_count: Optional[int] = None


class CRECBillReferenceInfo(BaseModel):
    crec_bill_reference_id: int
    legislation_id: Optional[int] = None
    cite_text: Optional[str] = None
    cite_type: Optional[str] = None
    start_offset: Optional[int] = None
    end_offset: Optional[int] = None


class CRECSpeechDetailInfo(CRECSpeechInfo):
    bill_references: List[CRECBillReferenceInfo] = []


class CRECGranuleDetailResponse(BaseModel):
    granule: CRECGranuleInfo
    speeches: List[CRECSpeechDetailInfo]
    summary: Optional[str] = None


class CRECSpeakerStatInfo(BaseModel):
    bioguide_id: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    party: Optional[str] = None
    state: Optional[str] = None
    image_url: Optional[str] = None
    total_words: int
    speech_count: int


class CRECSpeakerStatsResponse(BaseModel):
    speakers: List[CRECSpeakerStatInfo]
    total_results: int


class CRECActivityItem(BaseModel):
    date: date
    count: int


class CRECActivityResponse(BaseModel):
    activity: List[CRECActivityItem]
