from datetime import datetime
from typing import Any, Dict
from pydantic import BaseModel, ConfigDict

from weather_cases.environment.types import Level, OutputVar


class EnvironmentData(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    event_id: str
    timestamp: datetime
    level: Level
    # TODO: These should be GeoJSON, but that breaks OpenAPI docs
    data: Dict[OutputVar, Any | None]


class EnvironmentDataOverview(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    timestamp: datetime
    available_data: Dict[Level, list[OutputVar]]
