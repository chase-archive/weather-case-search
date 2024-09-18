from itertools import product
from matplotlib.contour import ContourSet
from matplotlib.path import Path
from geojson import GeoJSON

import numpy as np
import xarray as xr


def contour_linestrings(CS: ContourSet, digits: int = 2) -> GeoJSON:
    geojson_dict = {
        "type": "FeatureCollection",
    }
    features = []

    for level, path in zip(CS.levels, CS.get_paths()):
        segments = []
        for vertex, code in path.iter_segments():
            x, y = vertex
            next_coord = [round(float(x), digits), round(float(y), digits)]
            if code == Path.MOVETO:
                segments.append([next_coord])
            elif code == Path.LINETO and segments:
                segments[-1].append(next_coord)
            elif code == Path.CLOSEPOLY and segments:
                segments[-1].append(segments[-1][0])

        path_feats = [
            {
                "type": "Feature",
                "geometry": {"type": "LineString", "coordinates": segment},
                "properties": {"level": float(level)},
            }
            for segment in segments
        ]

        if path_feats:
            features += path_feats

    geojson_dict["features"] = features
    return GeoJSON(geojson_dict)


def contour_polygons(CS: ContourSet, digits: int = 2) -> GeoJSON:
    geojson_dict = {
        "type": "FeatureCollection",
    }
    features = []

    for level, path in zip(CS.levels, CS.get_paths()):
        segments = []
        for vertex, code in path.iter_segments():
            x, y = vertex
            next_coord = [round(float(x), digits), round(float(y), digits)]
            if code == Path.MOVETO:
                segments.append([next_coord])
            elif code == Path.LINETO and segments:
                segments[-1].append(next_coord)
            elif code == Path.CLOSEPOLY and segments:
                segments[-1].append(segments[-1][0])

        path_feats = [
            {
                "type": "Feature",
                "geometry": {"type": "Polygon", "coordinates": [segment]},
                "properties": {"level": float(level)},
            }
            for segment in segments
        ]

        if path_feats:
            features += path_feats

    geojson_dict["features"] = features
    return GeoJSON(geojson_dict)


def wind_vector_grid(u: xr.DataArray, v: xr.DataArray) -> GeoJSON:
    if u.shape != v.shape:
        raise ValueError("u and v are not the same shape")

    min_lat = int(np.floor(u.latitude.min().item()))
    max_lat = int(np.floor(u.latitude.max().item())) + 1
    min_lon = int(np.floor(u.longitude.min().item()))
    max_lon = int(np.floor(u.longitude.max().item())) + 1
    lats = range(min_lat, max_lat, 1)
    lons = range(min_lon, max_lon, 1)

    mag = np.sqrt(u**2 + v**2)
    dir = np.arctan2(v, -u)

    geojson_dict = {
        "type": "FeatureCollection",
    }
    features = []

    for lat, lon in product(lats, lons):
        try:
            wspd = mag.sel(latitude=lat, longitude=lon).item()
            wdir = dir.sel(latitude=lat, longitude=lon).item() * 180 / np.pi
        except KeyError:
            continue

        features.append(
            {
                "type": "Feature",
                "properties": {"wspd": wspd, "wdir": wdir},
                "geometry": {"coordinates": [lon, lat], "type": "Point"},
            }
        )

    geojson_dict["features"] = features
    return GeoJSON(geojson_dict)
