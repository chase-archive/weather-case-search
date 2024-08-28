from dataclasses import dataclass
from thefuzz import process

import pandas as pd

from weather_cases.extract import to_hash, to_searchable, to_weather_case
from weather_cases.models import WeatherCase


class WeatherCaseRegistry:
    def __init__(self):
        self._items = {}
        self._items_df = pd.DataFrame()

    @property
    def items(self):
        return self._items

    @items.setter
    def items(self, df: pd.DataFrame):
        searchable_items = {
            to_hash(row): RegistryElement(
                searchable=to_searchable(row),
                weather_case=to_weather_case(row),
                row=row,
            )
            for _, row in df.iterrows()
        }
        self._items = searchable_items
        self._items_df = df

    def search(self, q: str, min_score: int = 60):
        return process.extractBests(
            q,
            self._items.values(),
            limit=len(self._items),
            processor=fuzz_preprocess,
            score_cutoff=min_score,
        )

    def get_by_year(self, year: int):
        cases_by_year = self._items_df[self._items_df["DateTime"].dt.year == year]
        return [to_weather_case(row) for _, row in cases_by_year.iterrows()]


@dataclass
class RegistryElement:
    searchable: dict
    weather_case: WeatherCase
    row: pd.Series


def fuzz_preprocess(elem: RegistryElement | str):
    if isinstance(elem, str):
        return elem
    return elem.searchable
