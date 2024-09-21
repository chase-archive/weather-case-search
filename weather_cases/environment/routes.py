import asyncio
from datetime import datetime
import aiohttp
from fastapi import APIRouter, HTTPException


from weather_cases.environment import retrieve
from weather_cases.environment.configs import CONFIGS
from weather_cases.environment.models import EnvironmentData


router = APIRouter(prefix="/environment", tags=["environment"])


def _check_level(level: int):
    if level not in CONFIGS:
        raise HTTPException(status_code=400, detail="No data for level")


@router.get("/data/{event_id}/{timestamp}/{level}")
async def retrieve_environment(
    event_id: str,
    timestamp: datetime,
    level: int,
):
    _check_level(level)

    async with aiohttp.ClientSession() as http_client:
        results = await asyncio.gather(
            retrieve.height_contours(event_id, timestamp, level, http_client),
            retrieve.wind_plots(event_id, timestamp, level),
        )
        heights = results[0]
        wind = results[1]
        isotachs, wind_vectors = wind

        return EnvironmentData(
            event_id=event_id,
            timestamp=timestamp,
            level=level,
            height_contours=heights,
            isotachs=isotachs,
            wind_vectors=wind_vectors,
        )
