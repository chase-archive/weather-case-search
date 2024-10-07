from dataclasses import dataclass
import os
from typing import Dict
import numpy as np
import pandas as pd

from weather_cases.environment.contours import get_contour_calc
from weather_cases.environment.types import ContourSpec, Level, OutputVar


@dataclass
class Configs:
    level: Level
    height: ContourSpec = None
    isotachs: ContourSpec = None
    temps: ContourSpec = None
    dewpts: ContourSpec = None
    mslp: ContourSpec = None


CONFIGS: Dict[Level, Configs] = {
    200: Configs(
        level=200,
        height=get_contour_calc(include=12000, delta=60),
        isotachs=np.arange(50, 171, 2),
    ),
    300: Configs(
        level=300,
        height=get_contour_calc(include=9000, delta=60),
        isotachs=np.arange(50, 171, 2),
    ),
    500: Configs(
        level=500,
        height=get_contour_calc(include=5800, delta=60),
        isotachs=np.arange(20, 141, 2),
    ),
    700: Configs(
        level=700,
        height=get_contour_calc(include=3000, delta=30),
        isotachs=np.arange(20, 81, 2),
        temps=np.arange(-40, 31, 2),
    ),
    850: Configs(
        level=850,
        height=get_contour_calc(include=1500, delta=30),
        isotachs=np.arange(20, 81, 2),
        temps=np.arange(-40, 41, 2),
    ),
    "sfc": Configs(
        level="sfc",
        mslp=get_contour_calc(include=1000, delta=2),
        dewpts=np.arange(-40, 90, 1),  # degrees F
        isotachs=np.arange(10, 61, 1),
    ),
}


@dataclass(frozen=True)
class EventDataOutput:
    output_var: OutputVar
    filename: str
    filetype: str


OUTPUTS: Dict[OutputVar, EventDataOutput] = {
    "height": EventDataOutput("height", "heights", "geojson.gz"),
    "isotachs": EventDataOutput("isotachs", "wind", "zarr"),
    "barbs": EventDataOutput("barbs", "wind", "zarr"),
    "temperature": EventDataOutput("temperature", "temps", "zarr"),
    "dewpoint": EventDataOutput("dewpoint", "dewpts", "zarr"),
    "mslp": EventDataOutput("mslp", "mslp", "geojson.gz"),
}


@dataclass(frozen=True)
class EventDataRequest:
    event_id: str
    timestamp: pd.Timestamp
    level: Level

    def to_s3_folder(self) -> str:
        return f"v2/{self.event_id}/{self.timestamp:%Y-%m-%d}/{self.timestamp:%H}/{self.level}"

    def to_s3_location(self, kind: str, filetype: str) -> str:
        return f"{self.to_s3_folder()}/{kind}.{filetype}"

    def full_s3_folder_path(self) -> str:
        return f"s3://{os.getenv('S3_BUCKET_NAME')}/{self.to_s3_folder()}"

    def full_s3_location_path(self, kind: str, filetype: str) -> str:
        return (
            f"s3://{os.getenv('S3_BUCKET_NAME')}/{self.to_s3_location(kind, filetype)}"
        )
