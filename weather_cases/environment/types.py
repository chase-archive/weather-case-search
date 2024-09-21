import datetime
from typing import Tuple, Union
import pandas as pd


type Extent = Tuple[float, float, float, float]

type DateTimeLike = Union[str, pd.Timestamp, datetime.datetime, datetime.date]
