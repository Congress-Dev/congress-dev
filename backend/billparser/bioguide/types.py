# generated by datamodel-codegen:
#   filename:  genson_schema.json
#   timestamp: 2023-12-26T03:34:25+00:00

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel


class RelatedTo(BaseModel):
    usCongressBioId: str
    familyName: str
    givenName: str
    honorificPrefix: Optional[str] = None
    unaccentedFamilyName: str
    unaccentedGivenName: str
    birthDate: Optional[str] = None
    birthCirca: Optional[bool] = None
    deathDate: Optional[str] = None
    deathCirca: Optional[bool] = None
    middleName: Optional[str] = None
    unaccentedMiddleName: Optional[str] = None
    honorificSuffix: Optional[str] = None
    nickName: Optional[str] = None
    deleted: Optional[bool] = None
    birthDateUnknown: Optional[bool] = None
    deathDateUnknown: Optional[bool] = None


class RelationshipItem(BaseModel):
    relationshipType: str
    relatedTo: RelatedTo


class Job(BaseModel):
    name: str
    jobType: str


class Congress(BaseModel):
    name: str
    congressNumber: int
    congressType: str
    startDate: Optional[str] = None
    endDate: Optional[str] = None


class Party(BaseModel):
    name: str


class PartyAffiliationItem(BaseModel):
    party: Party
    startCirca: Optional[bool] = None
    endCirca: Optional[bool] = None
    startDate: Optional[str] = None
    startDateISO: Optional[str] = None
    endDate: Optional[str] = None
    endDateISO: Optional[str] = None


class CaucusAffiliationItem(BaseModel):
    party: Party
    startCirca: Optional[bool] = None
    endCirca: Optional[bool] = None
    startDate: Optional[str] = None
    startDateISO: Optional[str] = None
    endDate: Optional[str] = None
    endDateISO: Optional[str] = None


class Represents(BaseModel):
    regionType: str
    regionCode: str


class NoteItem(BaseModel):
    type: str
    noteType: str
    content: str


class CongressAffiliation(BaseModel):
    congress: Optional[Congress] = None
    partyAffiliation: Optional[List[PartyAffiliationItem]] = None
    caucusAffiliation: Optional[List[CaucusAffiliationItem]] = None
    represents: Optional[Represents] = None
    note: Optional[List[NoteItem]] = None
    departureReason: Optional[str] = None
    neverServed: Optional[bool] = None
    electionType: Optional[str] = None


class JobPosition(BaseModel):
    job: Job
    startDate: Optional[str] = None
    startCirca: Optional[bool] = None
    congressAffiliation: CongressAffiliation
    endCirca: Optional[bool] = None
    endDate: Optional[str] = None
    departureReason: Optional[str] = None
    deleted: Optional[bool] = None


class CreativeWorkItem(BaseModel):
    freeFormCitationText: str
    name: Optional[str] = None
    publishedDate: Optional[str] = None
    publishedDateISO: Optional[str] = None
    author: Optional[List[str]] = None
    publisher: Optional[str] = None


class Location(BaseModel):
    addressLocality: Optional[str] = None
    addressRegion: Optional[str] = None
    streetAddress: Optional[str] = None
    postalCode: Optional[str] = None


class ParentRecordLocation(BaseModel):
    name: str
    url: Optional[str] = None
    location: Location


class RecordLocation(BaseModel):
    name: str
    location: Location
    parentRecordLocation: Optional[ParentRecordLocation] = None
    url: Optional[str] = None


class ResearchRecordItem(BaseModel):
    name: Optional[str] = None
    recordType: Optional[List[str]] = None
    description: Optional[str] = None
    recordLocation: RecordLocation
    findingAid: Optional[bool] = None


class ImageItem(BaseModel):
    contentUrl: Optional[str] = None
    caption: Optional[str] = None


class NameHistoryItem(BaseModel):
    familyName: str
    givenName: str
    middleName: str
    duplicateName: bool
    startDate: str
    startCirca: bool
    endDate: str
    endCirca: bool


class BioGuideMember(BaseModel):
    usCongressBioId: str
    familyName: str
    givenName: str
    honorificPrefix: Optional[str] = None
    unaccentedFamilyName: str
    unaccentedGivenName: str
    birthDate: Optional[str] = None
    birthCirca: Optional[bool] = None
    deathDate: Optional[str] = None
    deathCirca: Optional[bool] = None
    profileText: Optional[str] = None
    relationship: Optional[List[RelationshipItem]] = []
    jobPositions: Optional[List[JobPosition]] = []
    creativeWork: Optional[List[CreativeWorkItem]] = []
    researchRecord: Optional[List[ResearchRecordItem]] = []
    nickName: Optional[str] = None
    image: Optional[List[ImageItem]] = None
    middleName: Optional[str] = None
    unaccentedMiddleName: Optional[str] = None
    honorificSuffix: Optional[str] = None
    deleted: Optional[bool] = None
    asset: Optional[List] = None
    nameHistory: Optional[List[NameHistoryItem]] = None
    deathDateUnknown: Optional[bool] = None
    birthDateUnknown: Optional[bool] = None
