from fastapi import FastAPI

from weather_cases.lifespan import lifespan, REGISTRY
from weather_cases.models import WeatherCase

app = FastAPI(lifespan=lifespan)


@app.get("/cases/search/")
def search_cases(q: str, limit: int = 5) -> list[WeatherCase]:
    items = REGISTRY.search(q)
    sorted_items = sorted(items, key=_sort_by_score_and_date, reverse=True)
    return [case.weather_case for i, (case, _) in enumerate(sorted_items) if i < limit]


def _sort_by_score_and_date(item):
    case, score = item
    return score, case.weather_case.timestamp
