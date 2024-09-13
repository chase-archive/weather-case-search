from dataclasses import dataclass

import numpy as np


@dataclass
class Configs:
    level: int
    height_contours: list[int] | None
    isotachs: list[int] | None


CONFIGS = {
    500: Configs(
        level=500,
        height_contours=np.arange(4680, 6100, 60),
        isotachs=np.arange(20, 141, 1),
    )
}
