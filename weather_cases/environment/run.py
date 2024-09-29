import pandas as pd

from weather_cases.environment import generate
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

    for dt, level, hght_field in generate.height_contours(extent, analysis_dts, levels):
        save_geojson(event_id, dt, level, "heights", hght_field)
        print(f"Processed heights {level} hPa at {dt}")

    for dt, level, wind in generate.wind_data(extent, analysis_dts, levels):
        save_dataset(event_id, dt, level, "wind", wind)
        print(f"Processed wind {level} hPa at {dt}")


if __name__ == "__main__":
    run_for(
        pd.Timestamp("1999-05-04T00:00:00"),
        "US",
        "3H",
    )
