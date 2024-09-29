from dataclasses import dataclass
import numpy as np

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
