from typing import Annotated, List, Optional
from pydantic import BaseModel, Field
from datetime import date

from congress_db.models import (
    Legislation,
    Legislator,
    LegislationChamber,
    UserUSCContentFolder,
    UserUSCContent,
    UserIdent
)
from congress_fastapi.models.legislation import LegislatorMetadata, LegislationMetadata
from congress_fastapi.models.abstract import MappableBase


class UserLoginRequest(BaseModel):
    access_token: str
    expires_in: int


class UserLoginResponse(MappableBase):
    user_id: Annotated[str, UserIdent.user_id]
    user_first_name: Annotated[str, UserIdent.user_first_name]
    user_last_name: Annotated[str, UserIdent.user_last_name]
    user_state: Annotated[Optional[str], UserIdent.user_state]

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

class UserStatsResponse(MappableBase):
    legislation: int
    versions: int
    legislators: int


# USC Tracking


class UserUSCContentFolder(MappableBase):
    user_usc_content_folder_id: Annotated[
        int, UserUSCContentFolder.user_usc_content_folder_id
    ]
    name: Annotated[str, UserUSCContentFolder.name]

