from typing import Annotated, List, Optional

from pydantic import BaseModel
from datetime import datetime

from billparser.db.models import (
    Legislation,
    LegislationVersion,
    Appropriation as AppropriationModel,
    LegislationVersionEnum,
    USCRelease,
)
from congress_fastapi.models.abstract import MappableBase


class Appropriation(MappableBase):
    """'appropriation_id': 'appropriation_id',
    'legislation_version_id': 'legislation_version_id',
    'amount': 'amount'"""

    appropriation_id: Annotated[int, AppropriationModel.appropriation_id]
    legislation_version_id: Annotated[int, AppropriationModel.legislation_version_id]
    amount: Annotated[Optional[float], AppropriationModel.amount]
    legislation_content_id: Annotated[int, AppropriationModel.legislation_content_id]
    fiscal_years: Annotated[List[int], AppropriationModel.fiscal_years]
    new_spending: Annotated[bool, AppropriationModel.new_spending]
    target: Annotated[Optional[str], AppropriationModel.target]

    until_expended: Annotated[bool, AppropriationModel.until_expended]
    expiration_year: Annotated[Optional[int], AppropriationModel.expiration_year]


class LegislationVersionMetadata(MappableBase):
    """ "legislation_id": "legislation_id",
    "legislation_version_id": "legislation_version_id",
    "effective_date": "effective_date",
    "created_at": "created_at",
    "legislation_version": "legislation_version","""

    legislation_id: Annotated[int, LegislationVersion.legislation_id]
    legislation_version_id: Annotated[int, LegislationVersion.legislation_version_id]
    effective_date: Annotated[Optional[datetime], LegislationVersion.effective_date]
    created_at: Annotated[datetime, LegislationVersion.created_at]
    legislation_version: Annotated[LegislationVersionEnum, LegislationVersion.legislation_version]


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
    congress: Annotated[int, Legislation.congress_id]

    # This comes from calculating the legislation_version
    usc_release_id: int
    legislation_versions: List[LegislationVersionMetadata]
    appropriations: List[Appropriation]
