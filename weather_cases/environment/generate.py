from typing import Iterable
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from geojson import GeoJSON

from weather_cases.environment.configs import CONFIGS, EventDataRequest
from weather_cases.environment.contours import get_contours
from weather_cases.environment.era5_rda import (
    CODES_PL,
    CODES_SFC,
    open_era5_pl_dataset,
    open_era5_sfc_dataset,
)
from weather_cases.environment.geojsons import contour_linestrings

from weather_cases.environment.types import Extent, XArrayData


def height_contours(
    extent: Extent, data_requests: Iterable[EventDataRequest]
) -> Iterable[tuple[EventDataRequest, GeoJSON]]:
    data_requests = [req for req in data_requests if req.level != "sfc"]
    unique_dates = set(req.timestamp.date() for req in data_requests)
    date_datasets = {
        d: open_era5_pl_dataset(d, CODES_PL["height"], subset=extent)
        for d in unique_dates
    }

    for req in data_requests:
        ds = date_datasets[req.timestamp.date()]
        if CONFIGS.get(req.level, None) and CONFIGS[req.level].height is not None:
            # calculate height from geopotential
            da = ds.sel(level=req.level, time=req.timestamp).Z / 9.8065
            da = _process_ds(da)

            x, y = np.meshgrid(da.longitude, da.latitude)
            contour_levels = get_contours(CONFIGS[req.level].height, da)  # type: ignore
            CS = plt.contour(x, y, da, levels=contour_levels)
            yield req, contour_linestrings(CS)


def wind_data(
    extent: Extent, data_requests: Iterable[EventDataRequest]
) -> Iterable[tuple[EventDataRequest, xr.Dataset]]:
    sfc_requests = [req for req in data_requests if req.level == "sfc"]
    unique_dates_sfc = set(req.timestamp.date() for req in sfc_requests)

    ua_requests = [req for req in data_requests if req.level != "sfc"]
    unique_dates_ua = set(req.timestamp.date() for req in ua_requests)

    u_datasets_ua = {
        d: open_era5_pl_dataset(d, CODES_PL["u"], subset=extent)
        for d in unique_dates_ua
    }
    v_datasets_ua = {
        d: open_era5_pl_dataset(d, CODES_PL["v"], subset=extent)
        for d in unique_dates_ua
    }
    # technically if dates are in the same month for the sfc datasets,
    # we don't need to open a ds per date, but performance doesn't matter here
    u_datasets_sfc = {
        d: open_era5_sfc_dataset(d, CODES_SFC["u"], subset=extent)
        for d in unique_dates_sfc
    }
    v_datasets_sfc = {
        d: open_era5_sfc_dataset(d, CODES_SFC["v"], subset=extent)
        for d in unique_dates_sfc
    }

    for req in data_requests:
        if req.level == "sfc":
            u_ds = u_datasets_sfc[req.timestamp.date()]
            v_ds = v_datasets_sfc[req.timestamp.date()]
        else:
            u_ds = u_datasets_ua[req.timestamp.date()]
            v_ds = v_datasets_ua[req.timestamp.date()]

        if CONFIGS.get(req.level, None) and CONFIGS[req.level].isotachs is not None:
            sel_kw = dict(time=req.timestamp)
            if req.level != "sfc":
                sel_kw["level"] = req.level  # type: ignore

            u = u_ds.sel(**sel_kw)  # type: ignore
            v = v_ds.sel(**sel_kw)  # type: ignore
            u = _process_ds(u)
            v = _process_ds(v)

            # convert to kt
            final_ds = xr.merge([u, v]) * 1.94384
            yield req, final_ds


def _process_ds(ds: XArrayData) -> XArrayData:
    ds_processed = ds.reindex(latitude=list(reversed(ds.latitude)))
    ds_processed.coords["longitude"] = (
        ds_processed.coords["longitude"] + 180
    ) % 360 - 180
    return ds_processed.sortby(ds_processed.longitude)
