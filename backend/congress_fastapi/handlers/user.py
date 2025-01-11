import requests
import base64
from datetime import datetime, timedelta
import hashlib

from sqlalchemy import select, update, join, delete, func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import aliased

from billparser.db.models import (
    User,
    Legislation,
    Legislator,
    UserLegislation,
    UserLegislator,
    LegislationSponsorship,
    LegislationVersion,
    Congress
)
from congress_fastapi.handlers.legislation.search import get_bill_sponsor
from congress_fastapi.db.postgres import get_database
from congress_fastapi.models.user import UserLoginResponse, UserLogoutResponse

GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


class InvalidTokenException(Exception):
    def __init__(self):
        self.name = ""

async def handle_get_user_legislation(cookie):
    if cookie is None:
        raise InvalidTokenException()

    user = await handle_get_user(cookie=cookie)

    database = await get_database()

    query = (
        select(UserLegislation.legislation_id)
        .where(UserLegislation.user_id == user.user_id)
    )

    results = await database.fetch_all(query)
    return {'legislation': [dict(x)['legislation_id'] for x in results]}

async def handle_get_user_legislator(cookie):
    if cookie is None:
        raise InvalidTokenException()

    user = await handle_get_user(cookie=cookie)

    database = await get_database()

    query = (
        select(UserLegislator.bioguide_id)
        .where(UserLegislator.user_id == user.user_id)
    )

    results = await database.fetch_all(query)
    return {'legislator': [dict(x)['bioguide_id'] for x in results]}

async def handle_get_user_legislation_update(cookie, legislation_id, action):
    legislation_id = int(legislation_id)

    if cookie is None:
        raise InvalidTokenException()

    user = await handle_get_user(cookie=cookie)

    database = await get_database()

    if action == 'add':
        query = insert(UserLegislation).values(legislation_id=legislation_id, user_id=user.user_id)
    elif action == 'remove':
        query = delete(UserLegislation).where(UserLegislation.legislation_id == legislation_id).where(UserLegislation.user_id == user.user_id)

    await database.execute(query)
    response = await handle_get_user_legislation(cookie)
    return response


async def handle_get_user_legislator_update(cookie, bioguide_id, action):
    if cookie is None:
        raise InvalidTokenException()

    user = await handle_get_user(cookie=cookie)

    database = await get_database()

    if action == 'add':
        query = insert(UserLegislator).values(bioguide_id=bioguide_id, user_id=user.user_id)
    elif action == 'remove':
        query = delete(UserLegislator).where(UserLegislator.bioguide_id == bioguide_id).where(UserLegislation.user_id == user.user_id)

    await database.execute(query)
    response = await handle_get_user_legislator(cookie)
    return response


async def handle_get_user_legislation_feed(cookie):
    if cookie is None:
        raise InvalidTokenException()

    database = await get_database()

    now = datetime.utcnow()
    seven_days_ago = now - timedelta(days=7)

    query = (
        select(
            Legislation.legislation_id,
            Legislation.title,
            Legislation.number,
            Congress.session_number,
            Legislation.legislation_type,
            Legislation.chamber,
            func.min(LegislationVersion.effective_date).label("effective_date")
        )
        .select_from(
            join(
                UserLegislation,
                Legislation,
                Legislation.legislation_id == UserLegislation.legislation_id,
            ).join(
                LegislationVersion,
                LegislationVersion.legislation_id == Legislation.legislation_id
            )
            .join(Congress, Congress.congress_id == Legislation.congress_id)
        )
        .group_by(
            Legislation.legislation_id,
            Legislation.title,
            Congress.session_number,
            Legislation.number,
            Legislation.congress_id,
            Legislation.legislation_type,
            Legislation.chamber,
        )
        .order_by(Legislation.number.desc())
        .where(LegislationVersion.effective_date >= seven_days_ago)
    )

    results = await database.fetch_all(query)

    legislation_ids = [result["legislation_id"] for result in results]
    sponsors_by_id = await get_bill_sponsor(legislation_ids)

    legislation = [{
        **dict(r),
        'sponsor': sponsors_by_id.get(r["legislation_id"], None)
    } for r in results]

    return {
        'legislation': legislation
    }


async def handle_get_user_legislator_feed(cookie):
    if cookie is None:
        raise InvalidTokenException()

    database = await get_database()

    now = datetime.utcnow()
    seven_days_ago = now - timedelta(days=7)

    query = (
        select(
            Legislation.legislation_id,
            Legislation.title,
            Legislation.number,
            Congress.session_number,
            Legislation.legislation_type,
            Legislation.chamber,
            func.min(LegislationVersion.effective_date).label("effective_date")
        ).select_from(
            join(
                UserLegislator,
                LegislationSponsorship,
                LegislationSponsorship.legislator_bioguide_id == UserLegislator.bioguide_id
            ).join(
                Legislation,
                Legislation.legislation_id == LegislationSponsorship.legislation_id
            ).join(
                LegislationVersion,
                LegislationVersion.legislation_id == Legislation.legislation_id
            ).join(
                Congress, Congress.congress_id == Legislation.congress_id
            )
        )
        .group_by(
            Legislation.legislation_id,
            Legislation.title,
            Congress.session_number,
            Legislation.number,
            Legislation.congress_id,
            Legislation.legislation_type,
            Legislation.chamber,
        )
        .order_by(Legislation.number.desc())
        .where(LegislationSponsorship.cosponsor == False)
        .where(LegislationVersion.effective_date >= seven_days_ago)
    )

    results = await database.fetch_all(query)

    legislation_ids = [result["legislation_id"] for result in results]
    sponsors_by_id = await get_bill_sponsor(legislation_ids)

    legislation = [{
        **dict(r),
        'sponsor': sponsors_by_id.get(r["legislation_id"], None)
    } for r in results]

    return {
        'legislation': legislation
    }


async def handle_get_user(cookie):
    if cookie is None:
        raise InvalidTokenException()

    database = await get_database()

    query = select(User).where(User.user_auth_cookie == cookie)
    result = await database.fetch_all(query)

    if len(result) > 0:
        return result[0]
    else:
        return None


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
            'user_auth_expiration': datetime.now() + timedelta(weeks=1),
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

    try:
        query = update(User)
        query = query.values(user_auth_cookie=None, user_auth_google=None, user_auth_expiration=None)
        query = query.where(User.user_auth_cookie == cookie)

        await database.execute(query)
    except Exception as e:
        pass

    return { 'success': True }