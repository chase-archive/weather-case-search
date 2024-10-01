from collections.abc import Callable, Iterable
import datetime
from typing import Literal, Tuple, Union
import pandas as pd
import xarray as xr


type Extent = Tuple[float, float, float, float]

type DateTimeLike = Union[str, pd.Timestamp, datetime.datetime, datetime.date]

type Level = int | Literal["sfc"]

type ContourSpec = Iterable[int] | ContourCalculation | None

type ContourCalculation = Callable[[xr.DataArray], Iterable[float]]

type XArrayData = xr.Dataset | xr.DataArray

type OutputVar = Literal[
    "height",
    "temperature",
    "dewpoint",
    "vorticity",
    "rh",
    "barbs",
    "isotachs",
    "mslp",
]
