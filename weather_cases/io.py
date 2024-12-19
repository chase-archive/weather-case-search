import os
from pathlib import Path
import re
import numpy as np
import pandas as pd

from weather_cases.extract import to_hash


def read_all_cases(with_id: bool = True) -> pd.DataFrame:
    parent = Path(__name__).parents[0].absolute()
    datadir = os.path.join(parent, "data")
    case_dfs = []

    for file in os.listdir(datadir):
        if not file.startswith("_") and (
            file.endswith(".csv") or file.endswith(".csv.gz")
        ):
            case_dfs.append(read_file(os.path.join(datadir, file), with_id=with_id))

    full_df = pd.concat(case_dfs)
    full_df.sort_values(by=["time_start"], ascending=False, inplace=True)
    return full_df


def read_file(file: str, with_id: bool, filter_incomplete: bool = True) -> pd.DataFrame:
    df = pd.read_csv(file, skiprows=[1])

    df["time_start"] = pd.to_datetime(
        df.time_start, format="%Y%m%d_%H%M", errors="coerce"
    )
    df["time_end"] = pd.to_datetime(df.time_end, format="%Y%m%d_%H%M", errors="coerce")
    df.rename(
        columns={c: re.sub(r"[\s/]+", "_", c.lower()) for c in df.columns}, inplace=True
    )

    if not filter_incomplete and with_id:
        raise ValueError("Incomplete data must be filtered out before generating id")

    if filter_incomplete:
        df = df[
            df.event_name.notnull()
            & df.time_start.notnull()
            & df.lat.notnull()
            & df.lon.notnull()
        ]

    if with_id:
        df["id"] = df.apply(to_hash, axis=1)

    for col in ["outbreak", "nickname", "user_comments"]:
        df[col] = df[col].str.replace(r'[\'"]', "", regex=True)

    df["event_name"] = df["event_name"].str.replace(r"-{2,}", "–", regex=True)
    df = df.replace({np.nan: None})
    return df
