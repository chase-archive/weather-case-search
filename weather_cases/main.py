from fastapi import FastAPI, HTTPException

from weather_cases.lifespan import lifespan, REGISTRY
from weather_cases.models import WeatherCase

app = FastAPI(lifespan=lifespan)


@app.get("/cases/search")
def search_cases(q: str, limit: int = 5) -> list[WeatherCase]:
    items = REGISTRY.search(q)
    sorted_items = sorted(items, key=_sort_by_score_and_date, reverse=True)
    return [case.weather_case for i, (case, _) in enumerate(sorted_items) if i < limit]


@app.get("/cases/{case_id}")
def get_case_by_id(case_id: str) -> WeatherCase:
    try:
        return REGISTRY.items[case_id].weather_case
    except KeyError:
        raise HTTPException(status_code=404, detail="Case not found")


def _sort_by_score_and_date(item):
    case, score = item
    return score, case.weather_case.timestamp
