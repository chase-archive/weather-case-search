# Chase Case Search

API to expose fuzzy search capability for storm chase cases.

### Prerequisites

* Python >= 3.12
* Docker (optional for development)
* [Poetry](https://python-poetry.org/)

After installing all prerequisites, run `poetry install`.

### Starting Locally

```
poetry run uvicorn weather_cases.main:app --reload --host localhost --port 8000
```

API docs available at localhost:8000/docs