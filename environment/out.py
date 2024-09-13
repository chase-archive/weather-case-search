from functools import partial
import gzip
import os
import geojson
import pandas as pd


def _opener(compress: bool) -> partial:
    return (
        partial(gzip.open, mode="wt", encoding="UTF-8")
        if compress
        else partial(open, mode="w")
    )


def filename_of(event_dt: pd.Timestamp, level: int, kind: str, compress: bool) -> str:
    return f"{event_dt:%Y%m%d%H}_{level}hPa_{kind}.geojson{'.gz' if compress else ''}"


def is_file(file: str) -> bool:
    return os.path.isfile(file)


def save_to_file(file: str, data: geojson.GeoJSON, compress=True) -> None:
    with _opener(compress=compress)(file) as f:
        geojson.dump(data, f)
