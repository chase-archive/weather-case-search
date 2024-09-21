from contextlib import asynccontextmanager
import os
from pathlib import Path

import aiohttp
from fastapi import FastAPI
import pandas as pd

from weather_cases.io import read_file
from weather_cases.registry import WeatherCaseRegistry

import matplotlib

matplotlib.use("Agg")


REGISTRY = WeatherCaseRegistry()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # load registry
    parent = Path(__name__).parents[0].absolute()
    datadir = os.path.join(parent, "data")
    case_dfs = []

    for file in os.listdir(datadir):
        if file.startswith("cases_") and file.endswith(".csv"):
            case_dfs.append(read_file(os.path.join(datadir, file)))

    full_df = pd.concat(case_dfs)
    full_df.sort_values(by=["DateTime"], ascending=False, inplace=True)
    REGISTRY.items = full_df

    # set up async http client
    app.state.http_client = aiohttp.ClientSession()

    yield
    if app.state.http_client:
        await app.state.http_client.close()
