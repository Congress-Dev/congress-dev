from typing import List
import requests
import base64
from datetime import datetime, timedelta
import hashlib
from typing import List

from sqlalchemy import select, update, join, delete, func, literal
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import aliased

from billparser.db.models import (
    USCContent,
    USCContentDiff,
    User,
    Legislation,
    Legislator,
    UserLegislation,
    UserLegislator,
    LegislationSponsorship,
    LegislationVersion,
    Congress,
    UserUSCContent,
    UserUSCContentFolder as UserUSCContentFolderDB,
)
from congress_fastapi.handlers.legislation.search import get_bill_sponsor
from congress_fastapi.db.postgres import get_database
from congress_fastapi.models.user import (
    UserLoginResponse,
    UserLogoutResponse,
    UserUSCContentFolder,
)

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

    user = await handle_get_user(cookie=cookie)

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
        .where(UserLegislation.user_id == user.user_id)
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

    user = await handle_get_user(cookie=cookie)

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
        .where(UserLegislator.user_id == user.user_id)
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


async def handle_get_user_stats(cookie):
    if cookie is None:
        raise InvalidTokenException

    user = await handle_get_user(cookie=cookie)

    database = await get_database()

    current_year = datetime.now().year
    first_day_of_year = datetime(current_year, 1, 1)



    legislation_count = await database.execute(
        select(
            func.count(func.distinct(Legislation.legislation_id)).label('count'),
        )
        .select_from(
            join(Legislation, LegislationVersion, Legislation.legislation_id == LegislationVersion.legislation_id)
        )
        .where(LegislationVersion.effective_date >= first_day_of_year))

    version_count = await database.execute(
        select(
            func.count(func.distinct(LegislationVersion.legislation_version_id)).label('count'),
        )
        .where(LegislationVersion.effective_date >= first_day_of_year))

    bioguide_count = await database.fetch_all(
        select(
            func.count(func.distinct(LegislationSponsorship.legislator_bioguide_id)).label('count'),
        )
        .select_from(
            join(Legislation, LegislationVersion, Legislation.legislation_id == LegislationVersion.legislation_id)
            .join(LegislationSponsorship, Legislation.legislation_id == LegislationSponsorship.legislation_id)
        )
        .where(LegislationVersion.effective_date >= first_day_of_year))

    return {
        "legislation": legislation_count or 0,
        "versions": version_count or 0,
        "legislators": len(bioguide_count) or 0,
    }


async def handle_get_usc_tracking_folders(user_id: str) -> List[UserUSCContentFolder]:
    database = await get_database()

    query = select(*UserUSCContentFolder.sqlalchemy_columns()).where(
        UserUSCContentFolderDB.user_id == user_id
    )

    results = await database.fetch_all(query)
    return [UserUSCContentFolder.from_sqlalchemy(result) for result in results]


async def handle_get_usc_tracking_results(user_id: str, folder_id: int):
    database = await get_database()
    query = (
        select(UserUSCContent.usc_ident)
        .where(UserUSCContent.user_id == user_id)
        .where(UserUSCContent.user_usc_content_folder_id == folder_id)
        .distinct()
        .as_scalar()
    )
    result = await database.fetch_all(query)
    idents = [x[0] for x in result]
    usc_content_alias = aliased(USCContent)
    usc_content_diff_alias = aliased(USCContentDiff)
    legislation_version_alias = aliased(LegislationVersion)
    legislation_alias = aliased(Legislation)

    query = (
        select(
            Legislation.legislation_id,
            Legislation.title,
            Legislation.number,
            Congress.session_number,
            Legislation.legislation_type,
            Legislation.chamber,
            func.min(LegislationVersion.effective_date).label("effective_date"),
        )
        .select_from(USCContent)
        .join(
            USCContentDiff,
            USCContentDiff.usc_content_id == USCContent.usc_content_id,
        )
        .join(
            LegislationVersion,
            USCContentDiff.version_id == LegislationVersion.version_id,
        )
        .join(
            Legislation,
            LegislationVersion.legislation_id
            == Legislation.legislation_id,
        )
        .join(Congress, Congress.congress_id == 2)
        .group_by(
            Legislation.legislation_id,
            Legislation.title,
            Congress.session_number,
            Legislation.number,
            Legislation.congress_id,
            Legislation.legislation_type,
            Legislation.chamber,
        )
        .where(or_(*[USCContent.usc_ident.ilike(ident) for ident in idents]))
        .where(Congress.congress_id == 2)
    )

    results = await database.fetch_all(query)
    legislation_ids = [result["legislation_id"] for result in results]
    sponsors_by_id = await get_bill_sponsor(legislation_ids)

    legislation = [
        {**dict(r), "sponsor": sponsors_by_id.get(r["legislation_id"], None)}
        for r in results
    ]

    return {"legislation": legislation}
