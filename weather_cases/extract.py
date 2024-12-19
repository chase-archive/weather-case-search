import hashlib
import re
import pandas as pd

from weather_cases.models import WeatherCase
from weather_cases.geog import get_state


def to_hash(row: pd.Series) -> str:
    summary = f"{row.event_name}_{row.time_start.date().isoformat()}"
    return hashlib.md5(summary.encode()).hexdigest()


def to_weather_case(row: pd.Series) -> WeatherCase:
    row_dict = row.to_dict()
    comma_sep_attrs = dict(
        tags=_to_list(row, "tags"),
        features=_to_list(row, "features"),
        records=_to_list(row, "records"),
        notes=_to_list(row, "notes"),
        user_comments=_to_list(row, "user_comments"),
        photo_video=_to_list(row, "photo_video"),
    )
    row_dict.update(comma_sep_attrs)

    return WeatherCase(
        **row_dict,
        id=to_hash(row),
    )


def to_searchable(row: pd.Series) -> dict:
    ret = {}
    ret.update(**location_attrs(row))
    ret.update(**date_attrs(row))
    ret.update(**misc_attrs(row))
    return ret


def location_attrs(row: pd.Series) -> dict:
    loc_cell = row["event_name"]
    loc_attrs = re.split(r"[–\-&/]+", loc_cell)
    loc_attrs.append(loc_cell)

    states = []
    for attr in loc_attrs:
        state_match = re.search(r"\b[A-Z]{2}\b", attr)
        if state_match:
            state_abbr = state_match.group(0)
            state = get_state(state_abbr)
            if state:
                states += [state_abbr, state]

    return dict(locations=loc_attrs, states=list(set(states)))


def date_attrs(row: pd.Series) -> dict:
    # TODO: convert to local time zone at lat lon - might need an API to do that
    dt = row["time_start"]
    ts_ctrl = pd.Timestamp(dt, tz="utc").tz_convert("America/Chicago")
    return {
        "date_reprs": [
            dt.isoformat(),
            ts_ctrl.strftime("%B %-d, %Y"),
            ts_ctrl.strftime("%B %Y"),
        ],
    }


def misc_attrs(row: pd.Series) -> dict:
    outbreak = row["outbreak"]

    return {
        "tags": _to_list(row, "tags"),
        "outbreak": outbreak,
    }


def concat_cols(row: pd.Series, cols: list[str]) -> list[str]:
    row_subset = row[cols]
    return [str(cell) for cell in row_subset if cell and str(cell).strip()]


def _to_list(row: pd.Series, col: str) -> list[str]:
    elem = row[col]
    if not elem:
        return []
    return [s.strip() for s in elem.split(",")]
