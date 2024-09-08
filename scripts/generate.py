from itertools import product
from typing import Iterable
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr
from geojson import GeoJSON

from scripts.era5_rda import open_era5_dataset, CODES
from scripts.geojsons import contour_linestrings


def height_contours(
    extent: tuple[float],
    times: Iterable[pd.Timestamp],
    levels: Iterable[int],
) -> Iterable[GeoJSON]:
    unique_dates = set(time.date() for time in times)
    date_datasets = (
        open_era5_dataset(d, CODES["height"], subset=extent, levels=list(levels))
        for d in unique_dates
    )
    for ds in date_datasets:
        for level, time in product(levels, times):
            if time in ds.time:
                da = ds.sel(level=level, time=time).Z / 9.8065
                x, y = np.meshgrid(da.longitude, da.latitude)
                CS = plt.contour(x, y, da, levels=np.arange(4680, 6100, 60))
                yield contour_linestrings(CS)


if __name__ == "__main__":
    from scripts import extents

    extent = extents.CONUS
    times = pd.date_range("2021-01-01", "2021-01-02", freq="6H")
    levels = (500, 700, 850)

    geojsons = list(height_contours(extent, times, levels))
    print(len(geojsons))
