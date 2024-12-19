from typing import Optional
from pydantic import BaseModel, Field

from datetime import datetime


class WeatherCase(BaseModel):
    id: str
    event_name: str
    time_start: datetime
    time_end: Optional[datetime] = Field(default=None)
    country: str
    lat: float
    lon: float
    magnitude: Optional[str] = Field(default=None)
    tags: list[str] = Field(default_factory=list)
    features: list[str] = Field(default_factory=list)
    records: list[str] = Field(default_factory=list)
    nickname: Optional[str] = Field(default=None)
    outbreak: Optional[str] = Field(default=None)
    notes: list[str] = Field(default_factory=list)
    user_comments: list[str] = Field(default_factory=list)
    photo_video: list[str] = Field(default_factory=list)
    account_summary: Optional[str] = Field(default=None)
