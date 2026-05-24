from airflow.sdk import dag, task
from datetime import timedelta
import polars as pl
from src.tools.data_cleaning import DataCleaning

filename_flight = "_flightdatas.parquet"
filename_weather = "_weatherdatas.parquet"

datas_path = "/opt/airflow/output"


@dag(
    dag_id='try_cleaning',
    description='A simple ETL pipeline',
    schedule=None,
    catchup=False,
    max_active_runs=1,
    default_args={
        "retries": 3,
        "retry_delay": timedelta(minutes=2),
    },
    tags=['test', 'cleaning'],
    doc_md="""
    Cleaning the datas
    """
)

def cleaning():
   
    @task
    def dataframe_loading():
        df_flights = pl.read_parquet(f"{datas_path}/*{filename_flight}")
        df_weather = pl.read_parquet(f"{datas_path}/*{filename_weather}")
        
        return print(DataCleaning(df_flights, df_weather).get_dataframe())
   
    dataframe_loading()

cleaning()