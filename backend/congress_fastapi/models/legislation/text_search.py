from typing import List, Optional

from pydantic import BaseModel, validator

MAX_RESULT_WINDOW = 100


class BillTextSearchRequest(BaseModel):
    query: str
    limit: int = 10
    cursor: Optional[str] = None

    # Metadata filters. Omit `version` to search across every version of a bill.
    congress: Optional[int] = None
    chamber: Optional[str] = None  # "House" | "Senate"
    bill_type: Optional[str] = None  # hr, s, hjres, sjres, hconres, sconres, hres, sres
    number: Optional[int] = None
    version: Optional[str] = None  # IH, RH, EH, ENR, ...
    legislation_id: Optional[int] = None
    legislation_version_id: Optional[int] = None

    # Upper bound on characters in each returned snippet.
    max_snippet_chars: int = 1200

    @validator("query")
    def query_not_blank(cls, v):
        if not v.strip():
            raise ValueError("query must not be empty")
        return v

    @validator("limit")
    def limit_in_range(cls, v):
        if not 1 <= v <= 50:
            raise ValueError("limit must be between 1 and 50")
        return v

    @validator("max_snippet_chars")
    def snippet_in_range(cls, v):
        if not 200 <= v <= 4000:
            raise ValueError("max_snippet_chars must be between 200 and 4000")
        return v


class BillTextHit(BaseModel):
    citation: str  # e.g. "H.R. 1234 (118th Congress) IH § SEC. 2"
    score: float  # cosine similarity, higher is better
    legislation_id: int
    legislation_version_id: int
    legislation_content_id: int
    lc_ident: Optional[str]
    congress: int
    chamber: str
    bill_type: str
    number: int
    version: str
    bill_title: str
    section_display: str
    heading: str
    snippet: str
    snippet_truncated: bool
    chunk_index: int
    chunk_count: int


class BillTextSearchResponse(BaseModel):
    hits: List[BillTextHit]
    next_cursor: Optional[str]
