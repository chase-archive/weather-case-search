from itertools import product
import pandas as pd

from weather_cases.environment import generate
from weather_cases.environment.configs import EventDataRequest
from weather_cases.environment.extents import EXTENTS
from weather_cases.environment.s3 import save_dataset, save_geojson


def find_datetime_range(event_dt: pd.Timestamp) -> tuple[pd.Timestamp, pd.Timestamp]:
    if 0 <= event_dt.hour < 6:
        start_dt = (event_dt - pd.Timedelta(1, "d")).replace(
            hour=12, minute=0, second=0
        )
    elif 6 <= event_dt.hour < 12:
        start_dt = (event_dt - pd.Timedelta(1, "d")).replace(
            hour=18, minute=0, second=0
        )
    elif 18 <= event_dt.hour < 24:
        start_dt = event_dt.replace(hour=12, minute=0, second=0)
    else:
        start_dt = event_dt.replace(hour=0, minute=0, second=0)

    return start_dt, start_dt + pd.Timedelta(21, "hours")


def run_for(event_dt: pd.Timestamp, country: str = "US", freq: str = "3H") -> None:
    event_id = "f901109b6613406f044b05fc145d491b"
    extent = EXTENTS[country]
    analysis_dts = pd.date_range(*find_datetime_range(event_dt), freq=freq)
    levels = (500,)

    data_requests = [
        EventDataRequest(event_id, dt, level)
        for dt, level in product(analysis_dts, levels)
    ]

    for req, hght_field in generate.height_contours(extent, data_requests):
        save_geojson(req, "heights", hght_field)
        print(f"Processed heights {req.level} hPa at {req.timestamp}")

    for req, wind in generate.wind_data(extent, data_requests):
        save_dataset(req, "wind", wind)
        print(f"Processed wind {req.level} hPa at {req.timestamp}")


if __name__ == "__main__":
    run_for(
        pd.Timestamp("1999-05-04T00:00:00"),
        "US",
        "3H",
    )
