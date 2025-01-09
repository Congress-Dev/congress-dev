import traceback
from typing import List, Optional
from billparser.db.models import User
from fastapi import APIRouter, HTTPException, Query, status, Response, Request

from congress_fastapi.handlers.user import handle_user_login, handle_user_logout, handle_get_user, InvalidTokenException
from congress_fastapi.models.errors import Error
from congress_fastapi.models.user import UserLoginRequest, UserLoginResponse, UserLogoutResponse

router = APIRouter()

@router.get(
    "/user"
)
async def user(request: Request) -> Optional[UserLoginResponse]:
    try:
        cookie = request.cookies.get("authentication")

        user = await handle_get_user(
            cookie=cookie
        )

    except InvalidTokenException:
        return None
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

    if user is not None:
        return UserLoginResponse(**user)


@router.post(
    "/user/login",
)
async def user_login(request: UserLoginRequest, response: Response) -> UserLoginResponse:
    try:
        user = await handle_user_login(
            access_token=request.access_token,
            expires_in=request.expires_in
        )

        response.set_cookie(key="authentication", value=user["user_auth_cookie"], max_age=request.expires_in)
    except InvalidTokenException:
        raise HTTPException(status_code=403, detail="Invalid or expired authentication token")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

    return UserLoginResponse(**user)


@router.get(
    "/user/logout"
)
async def user_logout(request: Request, response: Response) -> UserLogoutResponse:
    try:
        cookie = request.cookies.get("authentication")

        logout = await handle_user_logout(cookie)

        response.set_cookie(key="authentication", value=None, max_age=0)
    except InvalidTokenException:
        raise HTTPException(status_code=403, detail="Invalid or expired authentication token")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

    return UserLogoutResponse(**logout)