import re
import pandas as pd

from weather_cases.models import WeatherCase
from weather_cases.geog import get_state


def to_weather_case(row) -> WeatherCase:
    return WeatherCase(
        datetime=row["DateTime"],
        location=row["Location"],
        country=row["Country"],
        lat=float(row["lat"]),
        lon=float(row["lon"]),
        tor=row["TOR"],
        hail=row["HAIL"],
        wind=row["WIND"],
        cat=row["CAT"],
        tags=to_list(row, "Tags"),
        outbreak=row["Outbreak"],
        documentation=concat_cols(
            row, [col for col in row.index if "Documentation" in col]
        ),
        notes=row["Notes"],
    )


def to_searchable(row) -> dict:
    ret = {}
    ret.update(**location_attrs(row))
    ret.update(**date_attrs(row))
    ret.update(**misc_attrs(row))
    return ret


def location_attrs(row) -> dict:
    loc_cell = row["Location"]
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


def date_attrs(row) -> dict:
    # TODO: convert to local time zone at lat lon - might need an API to do that
    dt = row["DateTime"]
    ts_ctrl = pd.Timestamp(dt, tz="utc").tz_convert("America/Chicago")
    return {
        "date_reprs": [
            dt.isoformat(),
            ts_ctrl.strftime("%B %-d, %Y"),
            ts_ctrl.strftime("%B %Y"),
        ],
    }


def misc_attrs(row) -> dict:
    ef = row["TOR"]
    outbreak = row["Outbreak"]
    notes = row["Notes"]

    return {
        "tags": to_list(row, "Tags"),
        "ef": ef,
        "outbreak": outbreak,
        "notes": notes,
    }


def concat_cols(row, cols) -> str:
    row_subset = row[cols]
    return [str(cell) for cell in row_subset if cell and str(cell).strip()]


def to_list(row, col) -> list[str]:
    elem = row[col]
    if not elem:
        return []
    return [s.strip() for s in elem.split(",")]
