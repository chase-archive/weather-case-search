from dataclasses import dataclass
from typing import Iterable
import numpy as np


@dataclass
class Configs:
    level: int
    height_contours: Iterable[int] | None
    isotachs: Iterable[int] | None


CONFIGS = {
    500: Configs(
        level=500,
        height_contours=np.arange(4680, 6100, 60),
        isotachs=np.arange(20, 141, 5),
    )
}
