from datetime import datetime, timedelta

import pendulum
from airflow.sdk import dag, task

from src.extract_data.get_datas import GetDatas


@dag(
    dag_id="run_flight_extraction",
    description="A simple Extract pipeline",
    schedule="0 */3 * * *",
    start_date=pendulum.datetime(2026, 5, 8, tz=pendulum.timezone("Europe/Paris")),
    catchup=False,
    max_active_runs=1,
    default_args={
        "retries": 3,
        "retry_delay": timedelta(minutes=5),
    },
    tags=["elt", "extract"],
    doc_md="""
    Extract flight eatch 3 hours
    """,
)
def extractor():

    @task(task_id="extract_flight")
    def run_extraction():
        extractor = GetDatas(datetime.now().strftime("%Y-%m-%d")).get_flights(
            datetime.now().strftime("%H:00")
        )
        return extractor

    run_extraction()


extractor()
