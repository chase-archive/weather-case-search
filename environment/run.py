import pandas as pd

from environment.extents import EXTENTS
from environment.generate import heights, winds
from environment.out import save_to_s3


def run_for(event_dt: pd.Timestamp, country: str = "US", freq: str = "3H") -> None:
    extent = EXTENTS[country]
    if 0 <= event_dt.hour < 12:
        start_dt = (event_dt - pd.Timedelta(1, "d")).replace(hour=0, minute=0, second=0)
        end_dt = event_dt.replace(hour=12, minute=0, second=0)
    else:
        start_dt = event_dt.replace(hour=0, minute=0, second=0)
        end_dt = (event_dt + pd.Timedelta(1, "d")).replace(hour=12, minute=0, second=0)

    analysis_dts = pd.date_range(start=start_dt, end=end_dt, freq=freq)
    levels = (500,)

    for dt, level, hght_field in heights(extent, analysis_dts, levels):
        save_to_s3(dt, level, "heights", hght_field)
        print(f"Processed heights {level} hPa at {dt}")

    for dt, level, isotachs, barbs in winds(extent, analysis_dts, levels):
        save_to_s3(dt, level, "isotachs", isotachs)
        save_to_s3(dt, level, "barbs", barbs)
        print(f"Processed wind {level} hPa at {dt}")


if __name__ == "__main__":
    run_for(
        pd.Timestamp("1999-05-04T00:00:00"),
        "US",
        "3H",
    )
