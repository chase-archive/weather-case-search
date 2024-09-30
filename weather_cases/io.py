import os
from pathlib import Path
import numpy as np
import pandas as pd

from weather_cases.extract import to_hash


def read_all_cases(with_id: bool = True) -> pd.DataFrame:
    parent = Path(__name__).parents[0].absolute()
    datadir = os.path.join(parent, "data")
    case_dfs = []

    for file in os.listdir(datadir):
        if file.startswith("cases_") and file.endswith(".csv"):
            case_dfs.append(read_file(os.path.join(datadir, file), with_id=with_id))

    full_df = pd.concat(case_dfs)
    full_df.sort_values(by=["DateTime"], ascending=False, inplace=True)
    return full_df


def read_file(file: str, with_id: bool) -> pd.DataFrame:
    df = pd.read_csv(
        file, skiprows=[1], usecols=lambda c: "Unnamed" not in c and "Rating" not in c
    )
    df = df[
        df.DateTime.notnull()
        & df.Location.notnull()
        & df.lat.notnull()
        & df.lon.notnull()
    ]

    df["DateTime"] = pd.to_datetime(df.DateTime, format="%Y%m%d_%H%M")
    df["Outbreak"] = df["Outbreak"].str.replace('"', "")
    df["Notes"] = df["Notes"].str.replace('"', "")
    if with_id:
        df["id"] = df.apply(to_hash, axis=1)

    df = df.replace({np.nan: None})
    return df
