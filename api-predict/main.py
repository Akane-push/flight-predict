from fastapi import FastAPI, Request, Depends
from prometheus_fastapi_instrumentator import Instrumentator
from importlib import resources
import polars as pl
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from src.tools.api_key_auth import verify_api_key
from src.tools.api_rate_limiter import limiter, rate_limit_exceeded_handler
import json

# API init   ================================================
app = FastAPI()

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

Instrumentator().instrument(app).expose(app)

iata_path = resources.files("src.reference_data").joinpath("study_airport.json")

with iata_path.open("r", encoding="utf-8") as f:
    iata_list = json.load(f)

df_airports = pl.read_parquet(
    resources.files("src.reference_data").joinpath("airports_references.parquet")
)

airports_list = df_airports.filter(pl.col("Airport_IATA").is_in(iata_list))


@app.get("/available_airports")
def get_items(request: Request, api_key: str = Depends(verify_api_key)):
    return airports_list.to_dicts()
