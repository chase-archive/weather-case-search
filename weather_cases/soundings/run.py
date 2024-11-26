import json
import os
from pathlib import Path
from weather_cases.io import read_all_cases
from weather_cases.soundings.era5 import era5_sounding
from weather_cases.soundings.models import Profile


def load_soundings(from_idx: int, to_idx: int):
    all_cases = read_all_cases(with_id=True)
    cases_subset = all_cases.iloc[from_idx:to_idx]
    for _, case in cases_subset.iterrows():
        event_id = case["id"]
        event_dt = case["DateTime"]
        country = case["Country"]
        lat = case["lat"]
        lon = case["lon"]
        print(f"Processing case {event_id} from {event_dt} in {country}")

        sounding = era5_sounding(event_dt, lat, lon)

        loc = _get_output_loc(event_id)
        if loc:
            with open(loc, "w") as f:
                json.dump(_to_dict(sounding), f)


def _to_dict(sounding: Profile) -> dict:
    sounding_dict = dict(sounding)
    sounding_dict["lat"] = round(sounding_dict["lat"], 2)
    sounding_dict["lon"] = round(sounding_dict["lon"], 2)
    sounding_dict["timestamp"] = sounding_dict["timestamp"].isoformat()
    sounding_dict["data"] = dict(sounding_dict["data"])
    return sounding_dict


def _get_output_loc(name: str) -> str | bool:
    parent = Path(__name__).parents[1].absolute()
    outputloc = os.path.join(parent, "data", "soundings", name)

    if os.path.exists(outputloc):
        return False
    return outputloc
