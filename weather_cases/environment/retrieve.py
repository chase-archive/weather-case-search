import gzip
from io import BytesIO
import json
import os
from aiohttp import ClientSession
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from geojson import GeoJSON

from weather_cases.environment.configs import CONFIGS
from weather_cases.environment.contours import get_contours
from weather_cases.environment.geojsons import (
    contour_polygons,
    wind_vector_grid,
)
from weather_cases.environment.s3 import read_dataset, s3_location
from weather_cases.environment.types import DateTimeLike

load_dotenv()


async def wind_plots(
    event_id: str, dt: DateTimeLike, pressure_level: int
) -> tuple[GeoJSON, GeoJSON]:
    dt = pd.Timestamp(dt)
    ds = read_dataset(event_id, dt, pressure_level, "wind")

    u, v = ds.U, ds.V
    # eager load to avoid network round-trips, we will be using all coordinates
    u.load()
    v.load()

    pressure_level = ds.level.item()
    x, y = np.meshgrid(u.longitude, u.latitude)
    wspd = np.sqrt(u**2 + v**2)

    isotach_levels = get_contours(CONFIGS[pressure_level].isotachs, wspd)
    CS = plt.contourf(x, y, wspd, levels=isotach_levels)
    return contour_polygons(CS), wind_vector_grid(u, v)


async def height_contours(
    event_id: str, dt: DateTimeLike, pressure_level: int, client: ClientSession
) -> GeoJSON | None:
    cdn_url = os.getenv("ENVIRONMENT_DATA_CDN_URL")
    if not cdn_url:
        raise ValueError("CDN is not set")

    dt = pd.Timestamp(dt)
    data = s3_location(event_id, dt, pressure_level, "heights", "geojson.gz")

    async with client.get(f"{cdn_url}/{data}") as resp:
        if not resp.ok:
            return None

        gzipped_data = await resp.read()
        with gzip.GzipFile(fileobj=BytesIO(gzipped_data)) as gz:
            json_data = json.load(gz)

        return GeoJSON(json_data)
