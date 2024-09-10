from dataclasses import dataclass

import numpy as np


@dataclass
class Configs:
    height_contours: list[int]
    isotachs: list[int]


CONFIGS = {
    500: Configs(
        height_contours=np.arange(4680, 6100, 60), isotachs=np.arange(15, 145, 5)
    )
}
