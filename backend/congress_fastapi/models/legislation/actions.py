from typing import Annotated, List, Optional

from datetime import datetime

from billparser.db.models import (
    LegislationActionParse as LegislationActionParseModel,
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
    citations: Annotated[Optional[List[dict]], LegislationActionParseModel.citations] = []
