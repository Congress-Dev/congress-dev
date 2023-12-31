from typing import Annotated, List, Optional

from pydantic import BaseModel

from billparser.db.models import Legislation, LegislationSponsorship, Legislator
from congress_fastapi.models.abstract import MappableBase


class MemberInfo(MappableBase):
    bioguide_id: Annotated[str, Legislator.bioguide_id]
    first_name: Annotated[Optional[str], Legislator.first_name]
    last_name: Annotated[Optional[str], Legislator.last_name]
    middle_name: Annotated[Optional[str], Legislator.middle_name]


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
    number: Annotated[int, Legislation.number]
    title: Annotated[str, Legislation.title]


class LegislationSponsorshipList(BaseModel):
    legislation_sponsorships: List[LegislationSponsorshipInfo]
