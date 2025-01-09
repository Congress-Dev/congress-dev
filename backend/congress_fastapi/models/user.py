from typing import Annotated, List, Optional

from pydantic import BaseModel

from billparser.db.models import (
    User
)
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
