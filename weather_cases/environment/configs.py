from dataclasses import dataclass
import os
import numpy as np
import pandas as pd

from weather_cases.environment.contours import get_contour_calc
from weather_cases.environment.types import ContourSpec


@dataclass
class Configs:
    level: int
    height_contours: ContourSpec
    isotachs: ContourSpec


CONFIGS = {
    500: Configs(
        level=500,
        height_contours=get_contour_calc(include=5800, delta=60),
        isotachs=np.arange(20, 141, 2),
    )
}


@dataclass
class EventDataRequest:
    event_id: str
    timestamp: pd.Timestamp
    level: int

    def to_s3_folder(self) -> str:
        return f"{self.event_id}/{self.timestamp:%Y-%m-%d}/{self.timestamp:%H}/{self.level}"

    def to_s3_location(self, kind: str, filetype: str) -> str:
        return f"{self.to_s3_folder()}/{kind}.{filetype}"

    def full_s3_folder_path(self) -> str:
        return f"s3://{os.getenv('S3_BUCKET_NAME')}/{self.to_s3_folder()}"

    def full_s3_location_path(self, kind: str, filetype: str) -> str:
        return (
            f"s3://{os.getenv('S3_BUCKET_NAME')}/{self.to_s3_location(kind, filetype)}"
        )
