import numpy as np
import pandas as pd


def read_file(file) -> pd.DataFrame:
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

    df = df.replace({np.nan: None})
    return df
