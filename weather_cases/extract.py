import hashlib
import re
import pandas as pd

from weather_cases.models import WeatherCase
from weather_cases.geog import get_state


def to_hash(row: pd.Series) -> str:
    dt = row["DateTime"]
    lat = row["lat"]
    lon = row["lon"]
    summary = f'{dt.isoformat()}_{'%.2f' % round(float(lat), 2)}_{'%.2f' % round(float(lon), 2)}'
    return hashlib.md5(summary.encode()).hexdigest()


def to_weather_case(row: pd.Series) -> WeatherCase:
    return WeatherCase(
        id=to_hash(row),
        timestamp=row["DateTime"].to_pydatetime(),
        location=row["Location"],
        country=row["Country"],
        lat=float(row["lat"]),
        lon=float(row["lon"]),
        tags=to_list(row, "Tags"),
        outbreak=row["Outbreak"],
        documentation=concat_cols(
            row, [col for col in row.index if "Documentation" in col]
        ),
        notes=row["Notes"],
    )


def to_searchable(row: pd.Series) -> dict:
    ret = {}
    ret.update(**location_attrs(row))
    ret.update(**date_attrs(row))
    ret.update(**misc_attrs(row))
    return ret


def location_attrs(row: pd.Series) -> dict:
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


def date_attrs(row: pd.Series) -> dict:
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


def misc_attrs(row: pd.Series) -> dict:
    # most of the EF tor information is not entered in the data, 
    # it takes a little more effort to look that up
    # hence this will be skipped
    # ef = row["TOR"]

    # It's hard to distinguish useful vs. not useful notes.
    # We'll see if a column pops up that makes this useful
    # notes = row["Notes"]

    outbreak = row["Outbreak"]

    return {
        "tags": to_list(row, "Tags"),
        # "ef": ef,
        "outbreak": outbreak,
        # "notes": notes,
    }


def concat_cols(row: pd.Series, cols: list[str]) -> list[str]:
    row_subset = row[cols]
    return [str(cell) for cell in row_subset if cell and str(cell).strip()]


def to_list(row: pd.Series, col: str) -> list[str]:
    elem = row[col]
    if not elem:
        return []
    return [s.strip() for s in elem.split(",")]
