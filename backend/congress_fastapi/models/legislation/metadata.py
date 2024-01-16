from typing import Annotated, List, Optional

from pydantic import BaseModel

from billparser.db.models import Legislation, LegislationVersion
from congress_fastapi.models.abstract import MappableBase


class LegislationVersionMetadata(MappableBase):
    """ "legislation_id": "legislation_id",
    "legislation_version_id": "legislation_version_id",
    "effective_date": "effective_date",
    "created_at": "created_at",
    "legislation_version": "legislation_version","""

    legislation_id: Annotated[int, LegislationVersion.legislation_id]
    legislation_version_id: Annotated[int, LegislationVersion.legislation_version_id]
    effective_date: Annotated[str, LegislationVersion.effective_date]
    created_at: Annotated[str, LegislationVersion.created_at]
    legislation_version: Annotated[int, LegislationVersion.legislation_version]
    usc_release_id: Annotated[int, LegislationVersion.usc_release_id]


class LegislationMetadata(MappableBase):
    """'legislation_type': 'legislation_type',
    'number': 'number',
    'title': 'title',
    'legislation_id': 'legislation_id',
    'legislation_versions': 'legislation_versions',
    'congress': 'congress',
    'chamber': 'chamber',
    'usc_release_id': 'usc_release_id'"""

    legislation_id: Annotated[int, Legislation.legislation_id]
    legislation_type: Annotated[str, Legislation.legislation_type]
    number: Annotated[int, Legislation.number]
    title: Annotated[str, Legislation.title]
    legislation_versions: Annotated[List[str], Legislation.legislation_versions]
    congress: Annotated[int, Legislation.congress_id]

    # This comes from calculating the legislation_version
    usc_release_id: int
    legislation_versions: List[LegislationVersionMetadata]
