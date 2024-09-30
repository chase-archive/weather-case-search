from fastapi import HTTPException
from weather_cases.lifespan import REGISTRY
from weather_cases.models import WeatherCase

from fastapi import APIRouter

router = APIRouter(prefix="/cases", tags=["cases"])


@router.get("/search")
def search_cases(q: str, limit: int = 5) -> list[WeatherCase]:
    items = REGISTRY.search(q)
    sorted_items = sorted(items, key=_sort_by_score_and_date, reverse=True)
    return [case.weather_case for i, (case, _) in enumerate(sorted_items) if i < limit]


@router.get("/{case_id}")
def get_case_by_id(case_id: str) -> WeatherCase:
    try:
        return REGISTRY.items[case_id].weather_case
    except KeyError:
        raise HTTPException(status_code=404, detail="Case not found")


@router.get("/year/{year}")
def get_cases_by_year(year: int) -> list[WeatherCase]:
    return REGISTRY.get_by_year(year)


def _sort_by_score_and_date(item):
    case, score = item
    return score, case.weather_case.timestamp
