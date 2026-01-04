from typing import Annotated, List, Optional

from datetime import datetime

from congress_db.models import (
    LegislationContent as LegislationContentModel,
)
from congress_fastapi.models.abstract import MappableBase
from congress_fastapi.models.legislation.actions import LegislationActionParse
from pydantic import Field


class LegislationContent(MappableBase):
    """Model for the legislation content table"""

    legislation_content_id: Annotated[
        int, LegislationContentModel.legislation_content_id
    ] = Field(..., alias="legislation_content_id")
    legislation_version_id: Annotated[
        int, LegislationContentModel.legislation_version_id
    ] = Field(..., alias="legislation_version_id")
    parent_id: Annotated[Optional[int], LegislationContentModel.parent_id] = Field(..., alias="parent_id")
    lc_ident: Annotated[Optional[str], LegislationContentModel.lc_ident] = Field(..., alias="lc_ident")
    order_number: Annotated[int, LegislationContentModel.order_number] = Field(..., alias="order_number")
    section_display: Annotated[Optional[str], LegislationContentModel.section_display] = Field(..., alias="section_display")
    heading: Annotated[Optional[str], LegislationContentModel.heading]
    content_str: Annotated[Optional[str], LegislationContentModel.content_str] = Field(..., alias="content_str")
    content_type: Annotated[Optional[str], LegislationContentModel.content_type] = Field(..., alias="content_type")

    # To be filled in by the handler
    actions: Optional[List[LegislationActionParse]] = []
