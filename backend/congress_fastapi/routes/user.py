import traceback
from typing import List, Optional
from billparser.db.models import User
from fastapi import APIRouter, HTTPException, Query, status, Response, Request

from congress_fastapi.handlers.user import (
    handle_user_login,
    handle_user_logout,
    handle_get_user,
    handle_get_user_legislation,
    handle_get_user_legislator,
    handle_get_user_legislation_update,
    handle_get_user_legislator_update,
    InvalidTokenException
)
from congress_fastapi.models.errors import Error
from congress_fastapi.models.user import (
    UserLoginRequest,
    UserLoginResponse,
    UserLogoutResponse,
    UserLegislationResponse,
    UserLegislatorResponse,
    UserLegislationUpdateResponse,
    UserLegislatorUpdateResponse
)

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

@router.get(
    "/user/legislation"
)
async def user_legislation(request: Request) -> Optional[UserLegislationResponse]:
    try:
        cookie = request.cookies.get("authentication")

        user_legislation = await handle_get_user_legislation(
            cookie=cookie
        )

    except InvalidTokenException:
        return None
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

    if user_legislation is not None:
        return UserLegislationResponse(**user_legislation)

@router.get(
    "/user/legislation/update"
)
async def user_legislation_update(
    request: Request,
    legislation_id: str = Query(None),
    action: str = Query(None),
) -> UserLegislationResponse:
    try:
        cookie = request.cookies.get("authentication")

        user_legislation_update = await handle_get_user_legislation_update(
            cookie=cookie,
            legislation_id=legislation_id,
            action=action,
        )
    except InvalidTokenException:
        return None
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

    return UserLegislationResponse(**user_legislation_update)

@router.get(
    "/user/legislator"
)
async def user_legislator(request: Request) -> Optional[UserLegislatorResponse]:
    try:
        cookie = request.cookies.get("authentication")

        user_legislator = await handle_get_user_legislator(
            cookie=cookie
        )

    except InvalidTokenException:
        return None
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

    if user_legislator is not None:
        return UserLegislatorResponse(**user_legislator)

@router.get(
    "/user/legislator/update"
)
async def user_legislator_update(
    request: Request,
    legislator_id: str = Query(None),
    action: str = Query(None)
) -> UserLegislatorResponse:
    try:
        cookie = request.cookies.get("authentication")

        user_legislator_update = await handle_get_user_legislator_update(
            cookie=cookie,
            legislation_id=legislation_id,
            action=action,
        )
    except InvalidTokenException:
        return None
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

    return UserLegislatorResponse(**user_legislator_update)