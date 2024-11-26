import argparse
import json
import os
from weather_cases.io import read_all_cases
from weather_cases.soundings.era5 import era5_sounding
from weather_cases.soundings.models import Profile


def entrypoint():
    parser = argparse.ArgumentParser()
    parser.add_argument("from_idx", type=int)
    parser.add_argument("to_idx", type=int)
    args = parser.parse_args()
    load_soundings(args.from_idx, args.to_idx)


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

        loc = _get_output_loc(event_id)
        if not loc:
            print(f"Skipping {event_id} as it already exists")
        else:
            print(f"Saving {event_id} to {loc}")
            sounding = era5_sounding(event_dt, lat, lon)
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
    current_dir = os.path.dirname(os.path.abspath(__name__))
    output_loc = os.path.join(current_dir, "data", "soundings", f"{name}.json")

    if os.path.exists(output_loc):
        return False
    return output_loc
