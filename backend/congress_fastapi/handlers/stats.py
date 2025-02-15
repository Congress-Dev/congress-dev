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
    LegislationVersion
)
from congress_fastapi.db.postgres import get_database

async def handle_get_legislation_calendar():
    database = await get_database()

    current_year = datetime.now().year
    first_day_of_year = datetime(current_year, 1, 1)

    legislation_count = await database.fetch_all(
        select(
            func.count(LegislationVersion.legislation_version_id).label('value'),
            LegislationVersion.effective_date
        )
        .group_by(LegislationVersion.effective_date)
        .where(LegislationVersion.effective_date >= first_day_of_year))

    data = []
    for raw in legislation_count:
        data.append({
            'value': int(raw['value']),
            'day': raw['effective_date'].strftime("%Y-%m-%d")
        })

    return {'data': data}


async def handle_get_legislation_funnel():
    database = await get_database()

    version_lookup = {
        'ih': "Introduced",
        'is': "Introduced",
        'rfh': "Referred",
        'rfs': "Referred",
        'rds': "Received",
        'rhs': "Received",
        'rcs': "Reference Change",
        'rch': "Reference Change",
        'rs': "Reported",
        'rh': "Reported",
        'pcs': "Placed on Calendar",
        'pch': "Placed on Calendar",
        'cps': "Considered and Passed",
        'cph': "Considered and Passed",
        'eas': "Engrossed Amendment",
        'eah': "Engrossed Amendment",
        'es': "Engrossed",
        'eh': "Engrossed",
        'ras': "Referred w/Amendments",
        'rah': "Referred w/Amendments",
        'enr': "Enrolled",
    }

    current_year = datetime.now().year
    first_day_of_year = datetime(current_year, 1, 1)

    legislation_count = await database.fetch_all(
        select(
            func.count(LegislationVersion.legislation_version_id).label('value'),
            LegislationVersion.legislation_version
        )
        .group_by(LegislationVersion.legislation_version)
        .where(LegislationVersion.effective_date >= first_day_of_year))

    version_group = {}
    for raw in legislation_count:
        vid = raw['legislation_version'].lower()
        version = version_lookup[vid]
        if version in version_group:
            version_group[version] += raw['value']
        else:
            version_group[version] = raw['value']

    data = []
    for version_data in version_group:
        data.append({
            'id': version_data.lower().replace(" ", "_"),
            'value': version_group[version_data],
            'label': version_data
        })

    return {'data': data}
