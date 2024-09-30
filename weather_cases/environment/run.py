from itertools import product
import pandas as pd

from weather_cases.environment import generate
from weather_cases.environment.configs import EventDataRequest
from weather_cases.environment.extents import EXTENTS
from weather_cases.environment.overview import find_datetime_range
from weather_cases.environment.s3 import exists, save_dataset, save_geojson


def run_for(event_dt: pd.Timestamp, country: str = "US", freq: str = "3H") -> None:
    event_id = "f901109b6613406f044b05fc145d491b"
    extent = EXTENTS[country]
    analysis_dts = pd.date_range(*find_datetime_range(event_dt), freq=freq)
    levels = (500,)

    data_requests = [
        EventDataRequest(event_id, dt, level)
        for dt, level in product(analysis_dts, levels)
    ]
    hght_requests = [
        req for req in data_requests if not exists(req, "heights", "geojson.gz")
    ]
    wind_requests = [req for req in data_requests if not exists(req, "wind", "zarr")]

    for req, hght_field in generate.height_contours(extent, hght_requests):
        save_geojson(req, "heights", hght_field)
        print(f"Processed heights {req.level} hPa at {req.timestamp}")

    for req, wind in generate.wind_data(extent, wind_requests):
        save_dataset(req, "wind", wind)
        print(f"Processed wind {req.level} hPa at {req.timestamp}")


if __name__ == "__main__":
    run_for(
        pd.Timestamp("1999-05-04T00:00:00"),
        "US",
        "3H",
    )
