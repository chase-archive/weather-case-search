from typing import Iterable
import xarray as xr

from weather_cases.environment.configs import CONFIGS, EventDataRequest
from weather_cases.environment.era5 import arco_era5_isobaric
from weather_cases.environment.types import Extent, XArrayData


def complete_datasets(
    extent: Extent, data_requests: Iterable[EventDataRequest]
) -> Iterable[tuple[EventDataRequest, xr.Dataset]]:
    data_requests = set(data_requests)
    ds_parent = arco_era5_isobaric(subset=extent)

    height_dsets = dict(height_data(ds_parent, data_requests))
    wind_dsets = dict(wind_data(ds_parent, data_requests))

    for req in data_requests:
        print(f"Start generate data for {req}")
        datasets_for_req = []
        if height_dsets.get(req, None) is not None:
            datasets_for_req.append(height_dsets[req])
        if wind_dsets.get(req, None) is not None:
            datasets_for_req.append(wind_dsets[req])

        yield req, xr.merge(datasets_for_req, compat="override")


def height_data(
    ds_parent: xr.Dataset, data_requests: Iterable[EventDataRequest]
) -> Iterable[tuple[EventDataRequest, xr.DataArray]]:
    geopotential = ds_parent.geopotential.rename("Z")
    geopotential = _select_and_compute(geopotential, data_requests)

    for req in data_requests:
        if CONFIGS.get(req.level, None) and CONFIGS[req.level].height is not None:
            # calculate height from geopotential
            da = geopotential.sel(level=req.level, time=req.timestamp) / 9.8065
            da = _process_ds(da)

            print(f"Obtained height data for {req}")
            yield req, da  # type: ignore


def wind_data(
    ds_parent: xr.Dataset, data_requests: Iterable[EventDataRequest]
) -> Iterable[tuple[EventDataRequest, xr.Dataset]]:
    u_ds = ds_parent["u_component_of_wind"].rename("U")
    v_ds = ds_parent["v_component_of_wind"].rename("V")
    u_ds = _select_and_compute(u_ds, data_requests)
    v_ds = _select_and_compute(v_ds, data_requests)

    for req in data_requests:
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

            print(f"Obtained wind data for {req}")
            yield req, final_ds


def _process_ds(ds: XArrayData) -> XArrayData:
    ds_processed = ds.reindex(latitude=list(reversed(ds.latitude)))
    ds_processed.coords["longitude"] = (
        ds_processed.coords["longitude"] + 180
    ) % 360 - 180
    return ds_processed.sortby(ds_processed.longitude)


def _select_and_compute(
    ds: XArrayData, data_requests: Iterable[EventDataRequest]
) -> XArrayData:
    all_levels = set(req.level for req in data_requests)
    all_times = set(req.timestamp for req in data_requests)

    ds = ds.sel(level=list(all_levels), time=list(all_times))
    return ds.compute()
