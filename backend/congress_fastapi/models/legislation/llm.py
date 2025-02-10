from pydantic import BaseModel, field_validator


class LLMResponse(BaseModel):
    response: str
    tokens: int
    time: float


class LLMRequest(BaseModel):
    query: str


    # @field_validator("query")
    # def check_query_length(cls, query):
    #     if len(query) > 500:
    #         raise ValueError("Query is too long, must be less than 500 characters")
    #     return query