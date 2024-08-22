from typing import Optional
from pydantic import BaseModel, Field

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
    mag: Optional[str] = Field(default=None)
    tags: list[str]
    outbreak: Optional[str]
    documentation: list[str]
    event_summaries: list[str] = Field(default_factory=list)
    # TODO: this might be rennamed something else to incorporate all the columns
    notes: Optional[str] = Field(default=None)
