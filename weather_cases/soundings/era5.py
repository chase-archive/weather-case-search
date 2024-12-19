import warnings
import numpy as np
import pandas as pd
from weather_cases.environment.era5_rda import (
    CODES_PL,
    CODES_SFC,
    open_era5_pl_dataset,
    open_era5_sfc_dataset,
)
import weather_cases.soundings._metpy_override as mp
from weather_cases.soundings.models import Profile, ProfileData
from weather_cases.environment.types import DateTimeLike
from weather_cases.soundings.utils import nan_to_none, da_reversed


def era5_sounding(dt: DateTimeLike, lat: float, lon: float):
    if lon < 0:
        lon += 360

    # set the timestamp to the beginning of the hour
    # to avoid interpolation issues at 23:XX UTC
    dt = pd.Timestamp(dt).replace(minute=0)

    with warnings.catch_warnings(action="ignore"):
        # upper air data
        ds_hgt = open_era5_pl_dataset(dt, CODES_PL["height"], grid_spacing=0.25)
        ds_temp = open_era5_pl_dataset(dt, CODES_PL["temperature"], grid_spacing=0.25)
        ds_u = open_era5_pl_dataset(dt, CODES_PL["u"], grid_spacing=0.25)
        ds_v = open_era5_pl_dataset(dt, CODES_PL["v"], grid_spacing=0.25)
        ds_rh = open_era5_pl_dataset(dt, CODES_PL["rh"], grid_spacing=0.25)

        # surface data
        ds_sfc_temp = open_era5_sfc_dataset(
            dt, CODES_SFC["temperature"], grid_spacing=0.25
        )
        ds_sfc_dwpt = open_era5_sfc_dataset(
            dt, CODES_SFC["dewpoint"], grid_spacing=0.25
        )
        ds_sfc_u = open_era5_sfc_dataset(dt, CODES_SFC["u"], grid_spacing=0.25)
        ds_sfc_v = open_era5_sfc_dataset(dt, CODES_SFC["v"], grid_spacing=0.25)
        ds_sfc_p = open_era5_sfc_dataset(dt, CODES_SFC["sfcp"], grid_spacing=0.25)

        sfc_p = ds_sfc_p.SP.interp(latitude=lat, longitude=lon, time=dt).item() / 100
        sfc_hgt = (
            ds_hgt.Z.interp(latitude=lat, longitude=lon, time=dt, level=sfc_p).item()
            / mp.g
        )
        sfc_temp = (
            ds_sfc_temp.VAR_2T.interp(latitude=lat, longitude=lon, time=dt).item()
            - 273.15
        )
        sfc_dwpt = (
            ds_sfc_dwpt.VAR_2D.interp(latitude=lat, longitude=lon, time=dt).item()
            - 273.15
        )
        sfc_u = (
            ds_sfc_u.VAR_10U.interp(latitude=lat, longitude=lon, time=dt).item()
            * 1.94384
        )
        sfc_v = (
            ds_sfc_v.VAR_10V.interp(latitude=lat, longitude=lon, time=dt).item()
            * 1.94384
        )
        sfc_wspd = mp.wind_speed(sfc_u, sfc_v)
        sfc_wdir = mp.wind_direction(sfc_u, sfc_v)

        ds_ua_hgt = ds_hgt.Z.interp(latitude=lat, longitude=lon, time=dt) / mp.g
        ua_hgt = da_reversed(ds_ua_hgt[ds_ua_hgt.level < sfc_p])
        ua_lev = da_reversed(ds_ua_hgt.level[ds_ua_hgt.level < sfc_p])

        ds_ua_temp = ds_temp.T.interp(latitude=lat, longitude=lon, time=dt) - 273.15
        ua_temp = da_reversed(ds_ua_temp[ds_ua_temp.level < sfc_p])

        # RH is % but MetPy expects a decimal
        ds_ua_rh = np.clip(
            ds_rh.R.interp(latitude=lat, longitude=lon, time=dt) / 100, a_min=0, a_max=1
        )
        ds_ua_dwpt = mp.dewpoint_from_relative_humidity(ds_ua_temp, ds_ua_rh) - 273.15  # type: ignore
        ua_dwpt = da_reversed(ds_ua_dwpt[ds_ua_dwpt.level < sfc_p])  # type: ignore

        ds_ua_u = ds_u.U.interp(latitude=lat, longitude=lon, time=dt) * 1.94384
        ds_ua_v = ds_v.V.interp(latitude=lat, longitude=lon, time=dt) * 1.94384
        ds_wspd = mp.wind_speed(ds_ua_u, ds_ua_v)
        ds_wdir = mp.wind_direction(ds_ua_u, ds_ua_v)
        ua_wspd = da_reversed(ds_wspd[ds_wspd.level < sfc_p])  # type: ignore
        ua_wdir = da_reversed(ds_wdir[ds_wdir.level < sfc_p])  # type: ignore

        profile_lev = [sfc_p] + ua_lev
        profile_hgt = [sfc_hgt] + ua_hgt
        profile_temp = [sfc_temp] + ua_temp
        profile_dwpt = [sfc_dwpt] + ua_dwpt
        profile_wspd = [sfc_wspd] + ua_wspd
        profile_wdir = [sfc_wdir] + ua_wdir

        profile_data = ProfileData(
            level=nan_to_none(profile_lev),
            hght=nan_to_none(profile_hgt),
            temp=nan_to_none(profile_temp),
            dwpt=nan_to_none(profile_dwpt),
            wspd=nan_to_none(profile_wspd),  # type: ignore
            wdir=nan_to_none(profile_wdir),  # type: ignore
            omega=[],
        )

        return Profile(
            lat=lat,
            lon=lon,
            timestamp=pd.Timestamp(dt).to_pydatetime(),
            source='ERA5',
            data=profile_data,
        )
