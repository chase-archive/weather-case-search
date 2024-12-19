from itertools import product
import pandas as pd

from weather_cases.environment import generate
from weather_cases.environment.configs import OUTPUTS, EventDataRequest
from weather_cases.environment.extents import EXTENTS
from weather_cases.environment.overview import find_datetime_range
from weather_cases.environment.s3 import exists, save_dataset, save_geojson
from weather_cases.io import read_all_cases


def load_environments(limit: int | None = None) -> None:
    all_cases = read_all_cases(with_id=True)
    for idx, (_, case) in enumerate(all_cases.iterrows()):
        if limit is not None and idx >= limit:
            break

        event_id = case["id"]
        event_dt = case["time_start"]
        country = case["country"]

        extent = EXTENTS[country]
        analysis_dts = pd.date_range(*find_datetime_range(event_dt), freq="3h")
        levels = (200, 300, 500, 700, 850)

        data_requests = [
            EventDataRequest(event_id, dt, level)
            for dt, level in product(analysis_dts, levels)
        ]
        reqs_by_output = {}
        for output_var, output in OUTPUTS.items():
            reqs_by_output[output_var] = [
                req
                for req in data_requests
                if not exists(req, output.filename, output.filetype)
            ]

        for req, hght_field in generate.height_contours(
            extent, reqs_by_output["height"]
        ):
            save_geojson(req, OUTPUTS["height"].filename, hght_field)
            print(f"Processed heights {req.level} hPa at {req.timestamp}")

        all_wind_reqs = set(reqs_by_output["isotachs"] + reqs_by_output["barbs"])
        for req, wind in generate.wind_data(extent, all_wind_reqs):
            save_dataset(req, OUTPUTS["barbs"].filename, wind)
            print(f"Processed wind {req.level} hPa at {req.timestamp}")


if __name__ == "__main__":
    load_environments(limit=5)
