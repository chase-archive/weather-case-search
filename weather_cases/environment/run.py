from itertools import product
import pandas as pd

from weather_cases.environment import generate
from weather_cases.environment.configs import EventDataRequest
from weather_cases.environment.extents import EXTENTS
from weather_cases.environment.overview import find_datetime_range
from weather_cases.environment.s3 import keys, save_dataset
from weather_cases.io import read_all_cases


def load_environments(limit: int | None = None, overwrite: bool = False) -> None:
    all_cases = read_all_cases(with_id=True)
    for idx, (_, case) in enumerate(all_cases.iterrows()):
        if limit is not None and idx >= limit:
            break

        event_id = case["id"]
        event_dt = case["DateTime"]
        country = case["Country"]

        extent = EXTENTS[country]
        analysis_dts = pd.date_range(*find_datetime_range(event_dt), freq="3h")
        levels = (200, 300, 500, 700, 850)

        data_requests = (
            EventDataRequest(event_id, dt, level)
            for dt, level in product(analysis_dts, levels)
        )

        if not overwrite:
            existing_cases = set(keys(event_id))
            data_requests = (
                req
                for req in data_requests
                if not req.full_s3_location_path("all_data", "zarr") in existing_cases
            )

        for req, ds in generate.complete_datasets(extent, data_requests):
            save_dataset(req, "all_data", ds)
            print(f"Processed zarr {req.level} hPa at {req.timestamp}")


if __name__ == "__main__":
    load_environments(limit=5)
