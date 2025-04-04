from typing import List, Optional
from billparser.db.models import LegislationChamber, LegislationVersionEnum
from pydantic import BaseModel
from datetime import date

from congress_fastapi.models.legislation.metadata import (
    LegislationVersionMetadata,
    LegislatorMetadata,
)


class SearchResult(BaseModel):
    legislation_type: str
    number: int
    title: str
    legislation_id: int
    congress: str
    effective_date: Optional[date]
    chamber: LegislationChamber
    legislation_versions: List[LegislationVersionEnum]

    # Added on via subquery
    tags: List[str]
    summary: Optional[str]
    appropriations: Optional[float]
    sponsor: Optional[LegislatorMetadata]

    policy_areas: Optional[List[str]]
    subjects: Optional[List[str]]


class SearchResponse(BaseModel):
    legislation: List[SearchResult]
    total_results: int
