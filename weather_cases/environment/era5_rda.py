import numpy as np
import pandas as pd
import xarray as xr
from xarray.backends import PydapDataStore

from weather_cases.environment.types import DateTimeLike

CODES = {
    "height": "128_129_z.ll025sc",
    "temperature": "128_130_t.ll025sc",
    "u": "128_131_u.ll025uv",
    "v": "128_132_v.ll025uv",
    "omega": "128_135_w.ll025sc",
    "vorticity": "128_138_vo.ll025sc",
    "rh": "128_157_r.ll025sc",
}


def open_era5_dataset(
    date: DateTimeLike,
    code: str,
    subset: tuple[float, float, float, float] | None = None,
    grid_spacing: float = 0.5,
    levels: list[int] | None = None,
) -> xr.Dataset:
    date = pd.Timestamp(date)
    url = generate_rda_thredds_url(date, code)
    store = PydapDataStore.open(url, session=None)
    ds = xr.open_dataset(store)

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

    return ds.sel(**subset_dict)


def generate_rda_thredds_url(date: pd.Timestamp, code: str) -> str:
    base_url = (
        "https://thredds.rda.ucar.edu/thredds/dodsC/files/g/d633000/e5.oper.an.pl/"
    )
    file_name = f"e5.oper.an.pl.{code}.{date:%Y%m%d}00_{date:%Y%m%d}23.nc"
    return f"{base_url}{date:%Y%m}/{file_name}"
