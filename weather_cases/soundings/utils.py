import pandas as pd
import xarray as xr


def da_reversed(da: xr.DataArray) -> list[float]:
    return list(reversed(da.values.tolist()))


def nan_to_none(lst: list[float]) -> list[float | None]:
    return [v if not pd.isna(v) else None for v in lst]
