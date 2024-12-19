import warnings
import sounderpy as spy
import pandas as pd


import weather_cases.soundings._metpy_override as mp
from weather_cases.soundings.models import Profile, ProfileData
from weather_cases.environment.types import DateTimeLike
from weather_cases.soundings.utils import nan_to_none, da_reversed


def rapruc_sounding(dt: DateTimeLike, lat: float, lon: float):
    if lon < 0:
        lon += 360

    # set the timestamp to the beginning of the hour
    # to avoid interpolation issues at 23:XX UTC
    dt = pd.Timestamp(dt).replace(minute=0)

    # parse the dt obj into separate dt strs
    # to keep sounderpy happy
    year_str = str(dt.year)
    month_str = str(dt.month).zfill(2)
    day_str = str(dt.day).zfill(2)
    hour_str = str(dt.hour).zfill(2)

    with warnings.catch_warnings(action="ignore"):

        # load dictionary of profile data from SounderPy
        data_dict = spy.get_model_data('rap-ruc', [lat, lon], year_str, month_str, day_str, hour_str)

        # parse wind speed & direction from u and v
        wind_speed = mp.wind_speed(data_dict['u'], data_dict['v'])
        wind_direction = mp.wind_direction(data_dict['u'], data_dict['v'])

        profile_data = ProfileData(
            level=nan_to_none(data_dict['p'].m),
            hght=nan_to_none(data_dict['z'].m),
            temp=nan_to_none(data_dict['T'].m),
            dwpt=nan_to_none(data_dict['Td'].m),
            wspd=nan_to_none(wind_speed.m),  # type: ignore
            wdir=nan_to_none(wind_direction.m),  # type: ignore
            omega=nan_to_none(data_dict['omega'].m),
        )

        return Profile(
            lat=lat,
            lon=lon,
            timestamp=pd.Timestamp(dt).to_pydatetime(),
            source=data_dict['site_info']['model'],
            data=profile_data,
        )