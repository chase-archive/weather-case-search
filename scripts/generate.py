from typing import Iterable
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr
from geojson import GeoJSON

from scripts.era5_rda import open_era5_dataset, CODES
from scripts.geojsons import contour_linestrings, contour_polygons, wind_vector_grid


def heights(
    extent: tuple[float],
    times: Iterable[pd.Timestamp],
    pressure_level: int,
    contour_levels: list[int],
) -> Iterable[GeoJSON]:
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
            CS = plt.contour(x, y, da, levels=contour_levels)
            yield contour_linestrings(CS)


def winds(
    extent: tuple[float],
    times: Iterable[pd.Timestamp],
    pressure_level: int,
    contour_levels: list[int],
) -> Iterable[GeoJSON]:
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
            CS = plt.contour(x, y, wspd, levels=contour_levels)
            yield contour_polygons(CS), wind_vector_grid(u, v)


def _process_da(da: xr.DataArray) -> xr.DataArray:
    da_processed = da.reindex(latitude=list(reversed(da.latitude)))
    da_processed.coords["longitude"] = (
        da_processed.coords["longitude"] + 180
    ) % 360 - 180
    return da_processed.sortby(da_processed.longitude)


if __name__ == "__main__":
    from scripts import extents

    extent = extents.CONUS
    times = pd.date_range("2021-01-01", "2021-01-02", freq="6H")
    level = 500
    contour_levels = np.arange(20, 160, 5)

    geojsons = list(winds(extent, times, level, contour_levels))
    print(len(geojsons))
