from datetime import datetime
from pydantic import BaseModel
from geojson import GeoJSON

from weather_cases.environment.types import Level


class EnvironmentData(BaseModel):

    class Config:
        arbitrary_types_allowed = True

    event_id: str
    timestamp: datetime
    level: Level
    height_contours: GeoJSON | None
    isotachs: GeoJSON | None
    wind_vectors: GeoJSON | None
