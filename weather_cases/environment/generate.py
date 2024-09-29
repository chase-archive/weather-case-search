from typing import Iterable
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr
from geojson import GeoJSON

from weather_cases.environment.configs import CONFIGS, EventDataRequest
from weather_cases.environment.contours import get_contours
from weather_cases.environment.era5_rda import open_era5_dataset, CODES
from weather_cases.environment.geojsons import contour_linestrings

from weather_cases.environment.types import Extent, XArrayData


def height_contours(
    extent: Extent, data_requests: Iterable[EventDataRequest]
) -> Iterable[tuple[EventDataRequest, GeoJSON]]:
    unique_dates = set(req.timestamp.date() for req in data_requests)
    date_datasets = {
        d: open_era5_dataset(d, CODES["height"], subset=extent) for d in unique_dates
    }

    for req in data_requests:
        ds = date_datasets[req.timestamp.date()]
        if (
            CONFIGS.get(req.level, None)
            and CONFIGS[req.level].height_contours is not None
        ):
            # calculate height from geopotential
            da = ds.sel(level=req.level, time=req.timestamp).Z / 9.8065
            da = _process_ds(da)

            x, y = np.meshgrid(da.longitude, da.latitude)
            contour_levels = get_contours(CONFIGS[req.level].height_contours, da)  # type: ignore
            CS = plt.contour(x, y, da, levels=contour_levels)
            yield req, contour_linestrings(CS)


def wind_data(
    extent: Extent, data_requests: Iterable[EventDataRequest]
) -> Iterable[tuple[EventDataRequest, xr.Dataset]]:
    unique_dates = set(req.timestamp.date() for req in data_requests)
    u_datasets = {
        d: open_era5_dataset(d, CODES["u"], subset=extent) for d in unique_dates
    }
    v_datasets = {
        d: open_era5_dataset(d, CODES["v"], subset=extent) for d in unique_dates
    }

    for req in data_requests:
        u_ds = u_datasets[req.timestamp.date()]
        v_ds = v_datasets[req.timestamp.date()]
        if CONFIGS.get(req.level, None) and CONFIGS[req.level].isotachs is not None:
            # convert to kt
            u = u_ds.sel(level=req.level, time=req.timestamp)
            v = v_ds.sel(level=req.level, time=req.timestamp)
            u = _process_ds(u)
            v = _process_ds(v)

            final_ds = xr.merge([u, v]) * 1.94384
            yield req, final_ds


def _process_ds(ds: XArrayData) -> XArrayData:
    ds_processed = ds.reindex(latitude=list(reversed(ds.latitude)))
    ds_processed.coords["longitude"] = (
        ds_processed.coords["longitude"] + 180
    ) % 360 - 180
    return ds_processed.sortby(ds_processed.longitude)
