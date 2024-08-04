from contextlib import asynccontextmanager
import os
from pathlib import Path

from fastapi import FastAPI
import pandas as pd

from weather_cases.io import read_file
from weather_cases.registry import WeatherCaseRegistry


case_registry = WeatherCaseRegistry()


@asynccontextmanager
async def lifespan(app: FastAPI):
    parent = Path(__name__).parents[0].absolute()
    datadir = os.path.join(parent, "data")
    case_dfs = []

    for file in os.listdir(datadir):
        if file.startswith("cases_") and file.endswith(".csv"):
            case_dfs.append(read_file(os.path.join(datadir, file)))

    case_registry.items = pd.concat(case_dfs)
    yield
