from typing import Annotated, List, Optional
from congress_fastapi.models.legislation.actions import LegislationAction
from pydantic import root_validator
from datetime import datetime
import json

from billparser.db.models import (
    Legislation,
    LegislationVersion,
    LegislationVote,
    LegislationSponsorship,
    Appropriation as AppropriationModel,
    LegislationVersionEnum,
    USCRelease,
    LegislationContentTag,
    LegislationContentSummary,
    Legislator,
    LegislationVersionTag,
    LegislativePolicyArea,
    LegislativePolicyAreaAssociation,
    LegislativeSubject,
    LegislativeSubjectAssociation,
)
from congress_fastapi.models.abstract import MappableBase


class Appropriation(MappableBase):
    """'appropriation_id': 'appropriation_id',
    'legislation_version_id': 'legislation_version_id',
    'amount': 'amount'"""

    appropriation_id: Annotated[int, AppropriationModel.appropriation_id]
    parent_id: Annotated[Optional[int], AppropriationModel.parent_id]
    legislation_version_id: Annotated[int, AppropriationModel.legislation_version_id]
    amount: Annotated[Optional[float], AppropriationModel.amount]
    legislation_content_id: Annotated[int, AppropriationModel.legislation_content_id]
    fiscal_years: Annotated[Optional[List[int]], AppropriationModel.fiscal_years]
    new_spending: Annotated[bool, AppropriationModel.new_spending]
    target: Annotated[Optional[str], AppropriationModel.target]

    until_expended: Annotated[bool, AppropriationModel.until_expended]
    expiration_year: Annotated[Optional[int], AppropriationModel.expiration_year]
    brief_purpose: Annotated[Optional[str], AppropriationModel.purpose]


class LegislatorMetadata(MappableBase):
    legislator_id: Annotated[int, Legislator.legislator_id]
    bioguide_id: Annotated[str, Legislator.bioguide_id]
    first_name: Annotated[str, Legislator.first_name]
    middle_name: Annotated[Optional[str], Legislator.middle_name]
    last_name: Annotated[str, Legislator.last_name]
    party: Annotated[Optional[str], Legislator.party]
    state: Annotated[Optional[str], Legislator.state]
    district: Annotated[Optional[str], Legislator.district]
    image_url: Annotated[Optional[str], Legislator.image_url]
    image_source: Annotated[Optional[str], Legislator.image_source]
    profile: Annotated[Optional[str], Legislator.profile]

    cosponsor: Annotated[bool, LegislationSponsorship.cosponsor]


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
    legislation_version: Annotated[
        LegislationVersionEnum, LegislationVersion.legislation_version
    ]


class LegislationVoteMetadata(MappableBase):
    datetime: Annotated[str, LegislationVote.datetime]
    question: Annotated[str, LegislationVote.question]
    total: Annotated[dict, LegislationVote.total] = {}
    republican: Annotated[dict, LegislationVote.republican] = {}
    democrat: Annotated[dict, LegislationVote.democrat] = {}
    independent: Annotated[dict, LegislationVote.independent] = {}
    passed: Annotated[bool, LegislationVote.passed]

    @root_validator(pre=True)
    def parse_json(cls, values):
        if isinstance(values.get("total"), str):
            values["total"] = json.loads(values["total"])
        if isinstance(values.get("republican"), str):
            values["republican"] = json.loads(values["republican"])
        if isinstance(values.get("democrat"), str):
            values["democrat"] = json.loads(values["democrat"])
        if isinstance(values.get("independent"), str):
            values["independent"] = json.loads(values["independent"])
        return values


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

    sponsor: Optional[LegislatorMetadata]
    cosponsors: Optional[List[LegislatorMetadata]]

    votes: Optional[List[LegislationVoteMetadata]]

    policy_areas: Optional[List[str]]
    subjects: Optional[List[str]]
    actions: Optional[List[LegislationAction]]


class LegislationClauseTag(MappableBase):

    legislation_content_id: Annotated[int, LegislationContentTag.legislation_content_id]
    tags: Annotated[List[str], LegislationContentTag.tags]
    prompt_batch_id: Annotated[Optional[int], LegislationContentTag.prompt_batch_id]


class LegislationVersionTag(MappableBase):
    legislation_version_id: Annotated[int, LegislationVersionTag.legislation_version_id]
    tags: Annotated[List[str], LegislationVersionTag.tags]
    prompt_batch_id: Annotated[Optional[int], LegislationVersionTag.prompt_batch_id]


class LegislationClauseSummary(MappableBase):
    legislation_content_id: Annotated[
        int, LegislationContentSummary.legislation_content_id
    ]
    summary: Annotated[str, LegislationContentSummary.summary]
    prompt_batch_id: Annotated[Optional[int], LegislationContentSummary.prompt_batch_id]


class LegislationPolicyArea(MappableBase):
    name: Annotated[str, LegislativePolicyArea.name]


class LegislationSubject(MappableBase):
    subject: Annotated[str, LegislativeSubject.subject]
