from typing import Annotated, List, Optional
from pydantic import BaseModel, Field
from datetime import date

class NivoCalendarDatum(BaseModel):
    value: int
    day: str

class NivoCalendarResponse(BaseModel):
    data: List[NivoCalendarDatum]


class NivoFunnelDatum(BaseModel):
    id: str
    value: int
    label: str

class NivoFunnelResponse(BaseModel):
    data: List[NivoFunnelDatum]