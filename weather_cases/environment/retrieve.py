from typing import Dict
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr
from geojson import GeoJSON

from weather_cases.environment.configs import CONFIGS, EventDataRequest
from weather_cases.environment.contours import get_contours
from weather_cases.environment.geojsons import (
    contour_linestrings,
    contour_polygons,
    wind_vector_grid,
)
from weather_cases.environment.s3 import read_dataset
from weather_cases.environment.types import DateTimeLike, Level, OutputVar
from weather_cases.utils.timer import Timer

load_dotenv()


def environment_plots(
    event_id: str, timestamp: DateTimeLike, level: Level
) -> Dict[OutputVar, GeoJSON | None]:
    data_request = EventDataRequest(event_id, pd.Timestamp(timestamp), level)
    with Timer(identifier="reading dataset"):
        ds = read_dataset(data_request, "all_data")

    if ds is None:
        isotachs, barbs, heights = None, None, None
    else:
        ds.load()
        isotachs, barbs = wind_plots(ds, data_request)
        heights = height_contours(ds, data_request)

    return {"height": heights, "isotachs": isotachs, "barbs": barbs}


def wind_plots(
    ds: xr.Dataset, data_request: EventDataRequest
) -> tuple[GeoJSON | None, GeoJSON | None]:
    with Timer(identifier="get u and v wind components"):
        try:
            u, v = ds.U, ds.V
        except AttributeError:
            return None, None

    with Timer(identifier="generate isotachs and barbs"):
        x, y = np.meshgrid(u.longitude, u.latitude)
        wspd = np.sqrt(u**2 + v**2)

        pressure_level = data_request.level
        isotach_levels = get_contours(CONFIGS[pressure_level].isotachs, wspd)
        CS = plt.contourf(x, y, wspd, levels=isotach_levels)
        return contour_polygons(CS), wind_vector_grid(u, v)


def height_contours(ds: xr.Dataset, data_request: EventDataRequest) -> GeoJSON | None:
    with Timer(identifier="get height data"):
        try:
            da = ds.Z
        except AttributeError:
            return None

    with Timer(identifier="generate height contours"):
        x, y = np.meshgrid(da.longitude, da.latitude)

        pressure_level = data_request.level
        contour_levels = get_contours(CONFIGS[pressure_level].height, da)  # type: ignore
        CS = plt.contour(x, y, da, levels=contour_levels)
        return contour_linestrings(CS)
