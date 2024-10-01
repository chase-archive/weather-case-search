from collections.abc import Iterable
import pandas as pd

from weather_cases.environment.configs import OUTPUTS, EventDataRequest
from weather_cases.environment.models import EnvironmentDataOverview
from weather_cases.environment.s3 import keys
from weather_cases.environment.types import Level, OutputVar
from weather_cases.lifespan import REGISTRY


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


def event_available_data(event_id: str) -> list[EnvironmentDataOverview]:
    try:
        event_dt = REGISTRY.items[event_id].weather_case.timestamp
    except KeyError:
        return []
    start_dt, end_dt = find_datetime_range(pd.Timestamp(event_dt))
    event_dts = pd.date_range(start_dt, end_dt, freq="3h")

    return get_available_vars(event_id, event_dts)


def get_available_vars(
    event_id: str, timestamps: Iterable[pd.Timestamp]
) -> list[EnvironmentDataOverview]:
    levels = [200, 300, 500, 700, 850, "sfc"]
    ret = []

    try:
        items = set(f"s3://{k}" for k in keys(event_id))
    except FileNotFoundError:
        items = set()

    for timestamp in timestamps:
        outputs: dict[Level, list[OutputVar]] = {}
        for level in levels:
            outputs_for_level = []
            req = EventDataRequest(event_id, timestamp, level)

            for output_var, output in OUTPUTS.items():
                if req.full_s3_location_path(output.filename, output.filetype) in items:
                    outputs_for_level.append(output_var)

            outputs[level] = outputs_for_level

        ret.append(EnvironmentDataOverview(timestamp=timestamp, available_data=outputs))

    return ret
