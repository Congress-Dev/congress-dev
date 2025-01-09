import requests
import base64
from datetime import datetime, timedelta
import hashlib

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert

from billparser.db.models import User
from congress_fastapi.db.postgres import get_database
from congress_fastapi.models.user import UserLoginResponse, UserLogoutResponse

GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


class InvalidTokenException(Exception):
    def __init__(self):
        self.name = ""

async def handle_get_user(cookie):
    if cookie is None:
        raise InvalidTokenException()

    database = await get_database()

    query = select(User).where(User.user_auth_cookie == cookie)
    result = await database.fetch_all(query)

    return result[0]

async def handle_update_user_auth(user):
    database = await get_database()

    query = insert(User).values(**user)
    query = query.on_conflict_do_update(
        index_elements=['user_id'],
        set_={key: value for key, value in user.items() if key != 'user_id'}
    )
    await database.execute(query)

    return await handle_get_user(user['user_auth_cookie'])


async def handle_user_login(access_token: str, expires_in: int) -> UserLoginResponse:
    response = requests.get(GOOGLE_USERINFO_URL, headers={"Authorization": f"Bearer {access_token}"})

    if response.status_code == 200:
        response = response.json()

        md5_hash = hashlib.md5()
        md5_hash.update(access_token.encode("utf-8"))
        hash_result = md5_hash.hexdigest()

        image_response = requests.get(response['picture'])
        image_encoded = base64.b64encode(image_response.content).decode('utf-8')

        user = {
            'user_id': response['email'],
            'user_first_name': response['name'].replace(response['family_name'], '').strip(),
            'user_last_name': response['family_name'],
            'user_image': image_encoded,
            'user_auth_google': access_token,
            'user_auth_expiration': datetime.now() + timedelta(seconds=expires_in),
            'user_auth_cookie': hash_result,
        }

        user_query = await handle_update_user_auth(user)

        return {
            **user_query,
        }
    else:
        # Token is invalid or expired
        raise InvalidTokenException()


async def handle_user_logout(cookie) -> UserLogoutResponse:
    if cookie is None:
        raise InvalidTokenException()

    database = await get_database()

    query = update(User)
    query = query.values(user_auth_cookie=None, user_auth_google=None, user_auth_expiration=None)
    query = query.where(User.user_auth_cookie == cookie)

    print(query)

    await database.execute(query)

    return { 'success': True }