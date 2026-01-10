from typing import Annotated, List, Optional

from datetime import datetime

from congress_db.models import (
    LegislationActionParse as LegislationActionParseModel,
    LegislationAction as LegislationActionModel,
)
from congress_fastapi.models.abstract import MappableBase


class LegislationActionParse(MappableBase):
    """Model for the legislation action parse table"""

    legislation_action_parse_id: Annotated[
        int, LegislationActionParseModel.legislation_action_parse_id
    ]
    legislation_version_id: Annotated[
        int, LegislationActionParseModel.legislation_version_id
    ]
    legislation_content_id: Annotated[
        Optional[int], LegislationActionParseModel.legislation_content_id
    ]
    actions: Annotated[Optional[List[dict]], LegislationActionParseModel.actions] = []
    citations: Annotated[
        Optional[List[dict]], LegislationActionParseModel.citations
    ] = []


class LegislationAction(MappableBase):
    """
    API model for the `legislation_action` table
    """

    legislation_action_id: Annotated[int, LegislationActionModel.legislation_action_id]
    action_date: Annotated[datetime, LegislationActionModel.action_date]
    text: Annotated[str, LegislationActionModel.text]
    source_name: Annotated[str, LegislationActionModel.source_name]
