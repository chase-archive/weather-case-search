from typing import Optional
from pydantic import BaseModel

from datetime import datetime


class WeatherCase(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    id: str
    timestamp: datetime
    location: str
    country: str
    lat: float
    lon: float
    tor: Optional[str]
    hail: Optional[str]
    wind: Optional[str]
    cat: Optional[str]
    tags: list[str]
    outbreak: Optional[str]
    documentation: list[str]
    notes: Optional[str]
