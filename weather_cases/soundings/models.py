from datetime import datetime
from pydantic import BaseModel


class ProfileData(BaseModel):
    level: list[float | None]
    hght: list[float | None]
    temp: list[float | None]
    dwpt: list[float | None]
    wspd: list[float | None]
    wdir: list[float | None]
    omega: list[float | None]


class ProfileMetadata(BaseModel):
    lat: float
    lon: float
    timestamp: datetime


class Profile(ProfileMetadata):
    data: ProfileData
