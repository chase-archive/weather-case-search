from typing import Iterable
import xarray as xr

from weather_cases.environment.configs import CONFIGS, EventDataRequest
from weather_cases.environment.era5_rda import (
    CODES_PL,
    CODES_SFC,
    open_era5_pl_dataset,
    open_era5_sfc_dataset,
)
from weather_cases.environment.types import Extent, XArrayData


def complete_datasets(
    extent: Extent, data_requests: Iterable[EventDataRequest]
) -> Iterable[tuple[EventDataRequest, xr.Dataset]]:
    data_requests = set(data_requests)
    height_dsets = dict(height_data(extent, data_requests))
    wind_dsets = dict(wind_data(extent, data_requests))

    for req in data_requests:
        datasets_for_req = []
        if height_dsets.get(req, None):
            datasets_for_req.append(height_dsets[req])
        if wind_dsets.get(req, None):
            datasets_for_req.append(wind_dsets[req])

        yield req, xr.merge(datasets_for_req, compat="override")


def height_data(
    extent: Extent, data_requests: Iterable[EventDataRequest]
) -> Iterable[tuple[EventDataRequest, xr.Dataset]]:
    data_requests = [req for req in data_requests if req.level != "sfc"]
    unique_dates = set(req.timestamp.date() for req in data_requests)
    pl_datasets = {
        d: open_era5_pl_dataset(d, CODES_PL["height"], subset=extent)
        for d in unique_dates
    }
    for req in data_requests:
        ds = pl_datasets[req.timestamp.date()]
        if CONFIGS.get(req.level, None) and CONFIGS[req.level].height is not None:
            # calculate height from geopotential
            ds = ds.sel(level=req.level, time=req.timestamp) / 9.8065
            ds = _process_ds(ds)
            yield req, ds  # type: ignore


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
