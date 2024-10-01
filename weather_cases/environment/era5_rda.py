import numpy as np
import pandas as pd
import xarray as xr
from xarray.backends import PydapDataStore

from weather_cases.environment.types import DateTimeLike, Extent

RDA_THREDDS_BASE = "https://thredds.rda.ucar.edu/thredds/dodsC/files/g/d633000"

CODES_PL = {
    "height": "128_129_z.ll025sc",
    "temperature": "128_130_t.ll025sc",
    "u": "128_131_u.ll025uv",
    "v": "128_132_v.ll025uv",
    "vorticity": "128_138_vo.ll025sc",
}

CODES_SFC = {
    "mslp": "128_151_msl.ll025sc",
    "temperature": "128_167_2t.ll025sc",
    "dewpoint": "128_168_2d.ll025sc",
    "u": "128_165_10u.ll025sc",
    "v": "128_166_10v.ll025sc",
}


def open_era5_pl_dataset(
    date: DateTimeLike,
    code: str,
    subset: Extent | None = None,
    grid_spacing: float = 0.5,
    levels: list[int] | None = None,
) -> xr.Dataset:
    date = pd.Timestamp(date)
    url = generate_rda_pl_url(date, code)
    store = PydapDataStore.open(url, session=None)
    ds = xr.open_dataset(store)
    return ds.sel(**_get_subset_dict(subset, grid_spacing, levels))


def open_era5_sfc_dataset(
    date: DateTimeLike,
    code: str,
    subset: Extent | None = None,
    grid_spacing: float = 0.5,
    levels: list[int] | None = None,
) -> xr.Dataset:
    date = pd.Timestamp(date)
    url = generate_rda_sfc_url(date, code)
    store = PydapDataStore.open(url, session=None)
    ds = xr.open_dataset(store)
    return ds.sel(**_get_subset_dict(subset, grid_spacing, levels))


def generate_rda_pl_url(date: pd.Timestamp, code: str) -> str:
    base_url = f"{RDA_THREDDS_BASE}/e5.oper.an.pl/"
    file_name = f"e5.oper.an.pl.{code}.{date:%Y%m%d}00_{date:%Y%m%d}23.nc"
    return f"{base_url}{date:%Y%m}/{file_name}"


def generate_rda_sfc_url(date: pd.Timestamp, code: str) -> str:
    base_url = f"{RDA_THREDDS_BASE}/e5.oper.an.sfc/"
    month_start = date.replace(day=1)
    month_end = month_start + pd.offsets.MonthEnd(0)
    file_name = f"e5.oper.an.sfc.{code}.{month_start:%Y%m%d}00_{month_end:%Y%m%d}23.nc"
    return f"{base_url}{date:%Y%m}/{file_name}"


def _get_subset_dict(
    subset: Extent | None, grid_spacing: float, levels: list[int] | None
):
    subset_dict = {}
    if subset:
        x1, x2, y1, y2 = subset
        if x1 < 0:
            x1 += 360
        if x2 < 0:
            x2 += 360
        subset_dict["longitude"] = np.arange(x1, x2, grid_spacing)
        subset_dict["latitude"] = np.arange(y2, y1, -grid_spacing)

    if levels:
        subset_dict["level"] = levels

    return subset_dict
