from typing import Annotated, List, Optional
from pydantic import BaseModel, Field
from datetime import date

from billparser.db.models import (
    User,
    Legislation,
    Legislator,
    LegislationChamber
)
from congress_fastapi.models.legislation import LegislatorMetadata, LegislationMetadata
from congress_fastapi.models.abstract import MappableBase


class UserLoginRequest(BaseModel):
    access_token: str
    expires_in: int


class UserLoginResponse(MappableBase):
    user_id: Annotated[str, User.user_id]
    user_first_name: Annotated[str, User.user_first_name]
    user_last_name: Annotated[str, User.user_last_name]
    user_state: Annotated[Optional[str], User.user_state]

    user_image: Optional[str]

class UserLogoutResponse(MappableBase):
    success: bool

class UserLegislationMetadata(BaseModel):
    legislation_type: str
    number: int
    title: str
    legislation_id: int
    session_number: int
    effective_date: Optional[date]
    chamber: LegislationChamber
    sponsor: Optional[LegislatorMetadata]

class UserLegislationResponse(MappableBase):
    legislation: List[Annotated[int, Legislation.legislation_id]]

class UserLegislatorResponse(MappableBase):
    legislator: List[Annotated[str, Legislator.bioguide_id]]

class UserLegislationFeedResponse(MappableBase):
    legislation: List[UserLegislationMetadata]

class UserLegislatorFeedResponse(MappableBase):
    legislation: List[UserLegislationMetadata]

class UserLegislationUpdateResponse(MappableBase):
    success: bool

class UserLegislatorUpdateResponse(MappableBase):
    success: bool