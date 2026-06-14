import httpx
import datetime
from fastapi import FastAPI, HTTPException, Request, status, Depends
from typing import Any, Dict, Optional, Annotated
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
from src.api_tools.exception import validate_date_format, validate_time_format


airflow_url = os.getenv("AIRFLOW_API_URL")
dag_id_flight = "ad_hoc_flight"
dag_id_weather = "ad_hoc_weather"

# API init   ================================================
http_client: httpx.AsyncClient = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global http_client
    http_client = httpx.AsyncClient(
        base_url=airflow_url,
        timeout=5.0,
        limits=httpx.Limits(max_keepalive_connections=4, max_connections=5)
    )
    yield
    await http_client.aclose()

app = FastAPI(lifespan=lifespan)

# Connexion with Airflow API token   ================================================
security = HTTPBearer()

async def verify_airflow_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    token = credentials.credentials
    
    try:
        response = await http_client.get(
            "/api/v2/dags?limit=1", 
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == status.HTTP_401_UNAUTHORIZED:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="[WARNING] Invalid or expired Airflow token"
            )

        elif response.status_code == status.HTTP_403_FORBIDDEN:
            return token
            
        elif response.status_code != status.HTTP_200_OK:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"[WARNING] Airflow Auth Error [Status {response.status_code}]: {response.text}"
            )
            
        return token
        
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"[WARNING] Failed to connect to Airflow: {exc}"
        )

# Trigger flight dag  ================================================
@app.post("/trigger-ad_hoc-flight/{date_val}/{time_val}", status_code=status.HTTP_201_CREATED)
async def trigger_dag_flight(date_val: str, time_val: str, c_token: Annotated[str, Depends(verify_airflow_token)]):
    """Triggers the DAG
    Date format YYYY-MM-DD
    Time format HH:mm
    """
    validate_date_format(date_val)
    validate_time_format(time_val)

    now_utc = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    url = f"/api/v2/dags/{dag_id_flight}/dagRuns"
    headers = {
        "Authorization": f"Bearer {c_token}",
        "Content-Type": "application/json"
    }
    
    dag_run_data = {
            "logical_date": now_utc,
            "conf": {
                "date_val": date_val,
                "time_val": time_val
            }
        }

    try:
        response = await http_client.post(url, json=dag_run_data, headers={"Authorization": f"Bearer {c_token}"})

        if response.status_code not in [200, 201]:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"[WARNING] Airflow API error: {response.text}",
            )

        return response.json()

    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"[WARNING] Failed to connect to Airflow: {exc}",
        )

# Trigger weather dag  ================================================
@app.post("/trigger-ad_hoc-weather/{date_val}", status_code=status.HTTP_201_CREATED)
async def trigger_dag_weather(date_val: str, c_token: Annotated[str, Depends(verify_airflow_token)]):
    """Triggers the DAG
    Date format YYYY-MM-DD
    """
    validate_date_format(date_val)

    now_utc = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    url = f"/api/v2/dags/{dag_id_weather}/dagRuns"
    headers = {
        "Authorization": f"Bearer {c_token}",
        "Content-Type": "application/json"
    }
    
    dag_run_data = {
            "logical_date": now_utc,
            "conf": {
                "date_val": date_val
            }
        }

    try:
        response = await http_client.post(url, json=dag_run_data, headers={"Authorization": f"Bearer {c_token}"})

        if response.status_code not in [200, 201]:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"[WARNING] Airflow API error: {response.text}",
            )

        return response.json()

    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"[WARNING] Failed to connect to Airflow: {exc}",
        )
