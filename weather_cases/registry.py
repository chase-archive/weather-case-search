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

    def search(self, q: str, limit: int, min_score: int = 40):
        found = process.extract(
            q, self._items.values(), limit=limit, processor=fuzz_preprocess
        )
        for elem, score in found:
            if score >= min_score:
                yield elem.weather_case, score


@dataclass
class RegistryElement:
    searchable: dict
    weather_case: WeatherCase
    row: pd.Series


def fuzz_preprocess(elem: RegistryElement | str):
    if isinstance(elem, str):
        return elem
    return elem.searchable
