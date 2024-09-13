import pandas as pd

from environment.extents import EXTENTS
from environment.generate import heights, winds
from environment.out import filename_of, save_to_file


def run_for(
    event_dt: pd.Timestamp, country: str = "US", freq: str = "3H", compress: bool = True
):
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
        file = filename_of(dt, level, "heights", compress=compress)
        save_to_file(file, hght_field, compress=compress)
        print(f"Processed heights {level} hPa at {dt}")

    for dt, level, isotachs, barbs in winds(extent, analysis_dts, levels):
        file_isotachs = filename_of(dt, level, "isotachs", compress=compress)
        file_barbs = filename_of(dt, level, "barbs", compress=compress)
        save_to_file(file_isotachs, isotachs, compress=compress)
        save_to_file(file_barbs, barbs, compress=compress)
        print(f"Processed wind {level} hPa at {dt}")


if __name__ == "__main__":
    run_for(pd.Timestamp("1999-05-04T00:00:00"), "US", "3H", compress=True)
