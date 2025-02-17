from typing import Annotated, List, Optional

from pydantic import BaseModel

from billparser.db.models import (
    Legislation,
    LegislationSponsorship,
    Legislator,
    LegislationVersion,
    Congress,
)
from congress_fastapi.models.legislation import LegislationVersionMetadata
from congress_fastapi.models.abstract import MappableBase


class MemberInfo(MappableBase):
    bioguide_id: Annotated[str, Legislator.bioguide_id]
    first_name: Annotated[Optional[str], Legislator.first_name]
    last_name: Annotated[Optional[str], Legislator.last_name]
    middle_name: Annotated[Optional[str], Legislator.middle_name]
    party: Annotated[Optional[str], Legislator.party]
    state: Annotated[Optional[str], Legislator.state]
    job: Annotated[Optional[str], Legislator.job]

    image_url: Annotated[Optional[str], Legislator.image_url]
    image_source: Annotated[Optional[str], Legislator.image_source]
    profile: Annotated[Optional[str], Legislator.profile]

    twitter: Annotated[Optional[str], Legislator.twitter]
    facebook: Annotated[Optional[str], Legislator.facebook]
    youtube: Annotated[Optional[str], Legislator.youtube]
    instagram: Annotated[Optional[str], Legislator.instagram]


class MemberSearchInfo(MappableBase):
    bioguide_id: Annotated[str, Legislator.bioguide_id]
    first_name: Annotated[Optional[str], Legislator.first_name]
    last_name: Annotated[Optional[str], Legislator.last_name]
    middle_name: Annotated[Optional[str], Legislator.middle_name]
    party: Annotated[Optional[str], Legislator.party]
    state: Annotated[Optional[str], Legislator.state]
    job: Annotated[Optional[str], Legislator.job]

    image_url: Annotated[Optional[str], Legislator.image_url]


class MemberSearchResponse(BaseModel):
    members: List[MemberSearchInfo]
    total_results: int


class LegislationSponsorshipInfo(MappableBase):
    # This feeds the table on the member page so it only needs basic info
    legislation_sponsorship_id: Annotated[
        int, LegislationSponsorship.legislation_sponsorship_id
    ]
    # Sponsorship info
    legislation_id: Annotated[int, LegislationSponsorship.legislation_id]
    cosponsored: Annotated[bool, LegislationSponsorship.cosponsor]

    # Bill info
    chamber: Annotated[str, Legislation.chamber]
    congress: Annotated[int, Congress.session_number]
    number: Annotated[int, Legislation.number]
    title: Annotated[str, Legislation.title]


class LegislationSponsorshipList(MappableBase):
    legislation_sponsorships: List[LegislationSponsorshipInfo]
