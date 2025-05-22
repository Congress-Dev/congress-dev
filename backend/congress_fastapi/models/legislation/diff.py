from typing import Annotated, List, Optional

from datetime import datetime

from billparser.db.models import (
    USCContentDiff as USCContentDiffModel,
)
from congress_fastapi.models.abstract import MappableBase
from congress_fastapi.models.legislation.actions import LegislationActionParse
from pydantic import Field

class BillContentDiffMetadata(MappableBase):
    long_title: Optional[str] = None
    section_number: Optional[str] = None
    heading: Optional[str] = None
    display: Optional[str] = None
    short_title: Optional[str] = None
    repealed: Optional[bool] = None

class BillDiffMetadataList(MappableBase):
    legislation_version_id: int
    short_title: str
    long_title: str
    sections: List[BillContentDiffMetadata]
