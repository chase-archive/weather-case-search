from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from weather_cases.exceptions import DataNotFoundException
from weather_cases.lifespan import lifespan
from weather_cases.router import router as cases_router
from weather_cases.environment.router import router as environment_router
from weather_cases.soundings.router import router as soundings_router

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000, compresslevel=9)


@app.exception_handler(DataNotFoundException)
async def data_not_found_handler(request: Request, exc: DataNotFoundException):
    return JSONResponse(
        status_code=404,
        content={"message": "Not Found"},
    )


app.include_router(cases_router)
app.include_router(environment_router)
app.include_router(soundings_router)
