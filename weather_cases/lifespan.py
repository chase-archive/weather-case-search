from contextlib import asynccontextmanager

import aiohttp
from fastapi import FastAPI

from weather_cases.io import read_all_cases
from weather_cases.registry import WeatherCaseRegistry

import matplotlib


REGISTRY = WeatherCaseRegistry()


@asynccontextmanager
async def lifespan(app: FastAPI):
    REGISTRY.items = read_all_cases(with_id=False)

    matplotlib.use("Agg")

    # set up async http client
    app.state.http_client = aiohttp.ClientSession()

    yield
    if app.state.http_client:
        await app.state.http_client.close()
