# Because we can't install Metpy in a poetry environment
# see: https://github.com/Unidata/MetPy/issues/3700
import numpy as np
import numpy.typing as npt

g = 9.80665
Md = 28.96546e-3  # kg/mol
Mw = 18.01528e-3  # g/mol
epsilon = (Mw / 1000) / Md  # dimensionless
sat_pressure_0c = 6.112  # hPa
zero_degc = 273.15  # K


def dewpoint_from_relative_humidity(
    temperature: npt.ArrayLike, relative_humidity: npt.ArrayLike
) -> npt.ArrayLike:
    return dewpoint(relative_humidity * saturation_vapor_pressure(temperature))  # type: ignore


# temperature in celsius
def saturation_vapor_pressure(temperature: npt.ArrayLike) -> npt.ArrayLike:
    val = 17.67 * temperature / (temperature + 243.5)  # type: ignore
    return sat_pressure_0c * np.exp(val)


def dewpoint(vapor_pressure: npt.ArrayLike) -> npt.ArrayLike:
    val = np.log(vapor_pressure / sat_pressure_0c)  # type: ignore
    return zero_degc + 243.5 * val / (17.67 - val)


def mixing_ratio_from_specific_humidity(
    specific_humidity: npt.ArrayLike,
) -> npt.ArrayLike:
    return specific_humidity / (1 - specific_humidity)  # type: ignore


def dewpoint_from_specific_humidity(
    pressure: npt.ArrayLike, specific_humidity: npt.ArrayLike
) -> npt.ArrayLike:
    w = mixing_ratio_from_specific_humidity(specific_humidity)
    e = pressure * w / (epsilon + w)  # type: ignore
    return dewpoint(e)


def kelvin_to_celsius(kelvin: npt.ArrayLike) -> npt.ArrayLike:
    return kelvin - zero_degc  # type: ignore


def wind_speed(u: npt.ArrayLike, v: npt.ArrayLike) -> npt.ArrayLike:
    return np.sqrt(u**2 + v**2)  # type: ignore


def wind_direction(u: npt.ArrayLike, v: npt.ArrayLike) -> npt.ArrayLike:
    return 90 - np.arctan2(-v, -u) * 180 / np.pi  # type: ignore
