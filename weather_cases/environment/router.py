from datetime import datetime
from fastapi import APIRouter, HTTPException

from weather_cases.environment import retrieve
from weather_cases.environment.configs import CONFIGS
from weather_cases.environment.models import EnvironmentData, EnvironmentDataOverview
from weather_cases.environment.overview import event_available_data
from weather_cases.environment.types import Level


router = APIRouter(prefix="/environment", tags=["environment"])


def _check_level(level: Level) -> None:
    if level not in CONFIGS:
        raise HTTPException(status_code=404, detail="No data for level")


@router.get("/overview/{event_id}")
def retrieve_environment_overview(event_id: str) -> list[EnvironmentDataOverview]:
    return event_available_data(event_id)


@router.get("/data/{event_id}/{timestamp}/{level}")
def retrieve_environment(
    event_id: str,
    timestamp: datetime,
    level: Level,
) -> EnvironmentData:
    _check_level(level)
    data = retrieve.environment_plots(event_id, timestamp, level)

    return EnvironmentData(
        event_id=event_id, timestamp=timestamp, level=level, data=data
    )
