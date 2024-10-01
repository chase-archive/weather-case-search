import numpy as np
import xarray as xr

from collections.abc import Callable, Iterable

from weather_cases.environment.types import ContourCalculation, ContourSpec


def get_contour_calc(include: float, delta: float) -> ContourCalculation:
    def _calculate(da: xr.DataArray) -> Iterable[float]:
        modulo = include % delta
        da_min = da.min().item()
        da_max = da.max().item()
        start = (da_min // delta) * delta - (delta - modulo)
        end = da_max + delta
        return np.arange(start, end, delta)

    return _calculate


def get_contours(contour_spec: ContourSpec, da: xr.DataArray) -> Iterable[float]:
    if contour_spec is None:
        return []
    elif isinstance(contour_spec, Callable):
        return contour_spec(da)
    else:
        return contour_spec
