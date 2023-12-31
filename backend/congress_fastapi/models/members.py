from congress_fastapi.models.abstract import MappableBase
from billparser.db.models import Legislator
from typing import Annotated, Optional


class MemberInfo(MappableBase):
    bio_guide_id: Annotated[str, Legislator.bioguide_id]
    first_name: Annotated[Optional[str], Legislator.first_name]
    last_name: Annotated[Optional[str], Legislator.last_name]
    middle_name: Annotated[Optional[str], Legislator.middle_name]