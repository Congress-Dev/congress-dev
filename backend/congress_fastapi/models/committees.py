from typing import Annotated, Optional
from datetime import datetime

from billparser.db.models import (
    LegislationCommittee,
    LegislationChamber,
)
from congress_fastapi.models.abstract import MappableBase


class LegislationCommitteeInfo(MappableBase):
    """Pydantic model for LegislationCommittee"""

    legislation_committee_id: Annotated[
        int, LegislationCommittee.legislation_committee_id
    ]
    congress_id: Annotated[int, LegislationCommittee.congress_id]
    thomas_id: Annotated[Optional[str], LegislationCommittee.thomas_id]
    committee_id: Annotated[Optional[str], LegislationCommittee.committee_id]
    system_code: Annotated[Optional[str], LegislationCommittee.system_code]
    chamber: Annotated[Optional[LegislationChamber], LegislationCommittee.chamber]
    name: Annotated[Optional[str], LegislationCommittee.name]
    committee_type: Annotated[Optional[str], LegislationCommittee.committee_type]
    parent_id: Annotated[Optional[int], LegislationCommittee.parent_id]
    parent_name: Optional[str] = None
    url: Annotated[Optional[str], LegislationCommittee.url]
    minority_url: Annotated[Optional[str], LegislationCommittee.minority_url]
    address: Annotated[Optional[str], LegislationCommittee.address]
    phone: Annotated[Optional[str], LegislationCommittee.phone]
    rss_url: Annotated[Optional[str], LegislationCommittee.rss_url]
    jurisdiction: Annotated[Optional[str], LegislationCommittee.jurisdiction]
    youtube_id: Annotated[Optional[str], LegislationCommittee.youtube_id]


class LegislationCommitteeSearchResponse(MappableBase):
    """Response model for committee search"""

    committees: list[LegislationCommitteeInfo]
    total_results: int
