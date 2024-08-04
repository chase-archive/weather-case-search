from dataclasses import dataclass
from thefuzz import process

import pandas as pd

from weather_cases.extract import to_checksum, to_searchable, to_weather_case
from weather_cases.models import WeatherCase


class WeatherCaseRegistry:
    def __init__(self):
        self._items = {}

    @property
    def items(self):
        return self._items

    @items.setter
    def items(self, df: pd.DataFrame):
        searchable_items = {
            to_checksum(row): RegistryElement(
                searchable=to_searchable(row),
                weather_case=to_weather_case(row),
                row=row,
            )
            for _, row in df.iterrows()
        }
        self._items = searchable_items

    def search(self, q: str, min_score: int = 50):
        return process.extractBests(
            q,
            self._items.values(),
            limit=len(self._items),
            processor=fuzz_preprocess,
            score_cutoff=min_score,
        )


@dataclass
class RegistryElement:
    searchable: dict
    weather_case: WeatherCase
    row: pd.Series


def fuzz_preprocess(elem: RegistryElement | str):
    if isinstance(elem, str):
        return elem
    return elem.searchable
