from typing import Iterable
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr
from geojson import GeoJSON

from environment.contours import CONFIGS
from environment.era5_rda import open_era5_dataset, CODES
from environment.geojsons import contour_linestrings, contour_polygons, wind_vector_grid


def heights(
    extent: tuple[float],
    times: Iterable[pd.Timestamp],
    pressure_level: int,
) -> Iterable[GeoJSON]:
    if not CONFIGS.get(pressure_level):
        raise ValueError("Invalid pressure level")

    config = CONFIGS[pressure_level]
    if not len(config.height_contours):
        return

    unique_dates = set(time.date() for time in times)
    date_datasets = (
        open_era5_dataset(d, CODES["height"], subset=extent) for d in unique_dates
    )
    for ds in date_datasets:
        for time in (t for t in times if t in ds.time):
            # calculate height from geopotential
            da = ds.sel(level=pressure_level, time=time).Z / 9.8065
            da = _process_da(da)

            x, y = np.meshgrid(da.longitude, da.latitude)
            CS = plt.contour(x, y, da, levels=config.height_contours)
            yield contour_linestrings(CS)


def winds(
    extent: tuple[float],
    times: Iterable[pd.Timestamp],
    pressure_level: int,
) -> Iterable[tuple[GeoJSON, GeoJSON]]:
    if not CONFIGS.get(pressure_level):
        raise ValueError("Invalid pressure level")

    config = CONFIGS[pressure_level]
    if not len(config.isotachs):
        return

    unique_dates = set(time.date() for time in times)
    u_datasets = (open_era5_dataset(d, CODES["u"], subset=extent) for d in unique_dates)
    v_datasets = (open_era5_dataset(d, CODES["v"], subset=extent) for d in unique_dates)

    for u_ds, v_ds in zip(u_datasets, v_datasets):
        for time in (t for t in times if t in u_ds.time):
            # convert to kt
            u = u_ds.sel(level=pressure_level, time=time).U * 1.94384
            v = v_ds.sel(level=pressure_level, time=time).V * 1.94384
            u = _process_da(u)
            v = _process_da(v)

            x, y = np.meshgrid(u.longitude, u.latitude)
            wspd = np.sqrt(u**2 + v**2)
            CS = plt.contourf(x, y, wspd, levels=config.isotachs)
            yield contour_polygons(CS), wind_vector_grid(u, v)


def _process_da(da: xr.DataArray) -> xr.DataArray:
    da_processed = da.reindex(latitude=list(reversed(da.latitude)))
    da_processed.coords["longitude"] = (
        da_processed.coords["longitude"] + 180
    ) % 360 - 180
    return da_processed.sortby(da_processed.longitude)
