import httpx
from fastapi import FastAPI, HTTPException, Request, status
from dotenv import load_dotenv
import json
from importlib import resources
import polars as pl

app = FastAPI()

iata_path = resources.files("src.reference_data").joinpath("study_airport.json")

with iata_path.open("r", encoding="utf-8") as f:
    iata_list = json.load(f)

df_airports = pl.read_parquet(resources.files("src.reference_data").joinpath("airports_references.parquet"))

airports_list = df_airports.filter(pl.col("Airport_IATA").is_in(iata_list))

@app.get("/available_airports")
def get_items():
    return airports_list.to_dicts()