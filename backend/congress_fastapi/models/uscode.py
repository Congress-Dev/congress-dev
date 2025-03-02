from pydantic import BaseModel
from pydantic import validator


class USCodeSearchRequest(BaseModel):
    query: str
    results: int

    @validator("results")
    def results_must_be_valid(cls, v):
        if not 1 <= v <= 20:
            raise ValueError("Results must be a positive integer not greater than 20")
        return v

class USCodeSearchResponse(BaseModel):
    usc_link: str
    section_display: str
    title: str