from datetime import timedelta

import pendulum
from airflow.providers.standard.operators.bash import BashOperator
from airflow.sdk import dag, task

from src.tools.XGBoost_GridSearch import XGBGridSearch


@dag(
    dag_id="training_model",
    description="Launch training model",
    schedule="0 2 * * 0",
    start_date=pendulum.datetime(2024, 5, 10, tz=pendulum.timezone("Europe/Paris")),
    catchup=False,
    max_active_runs=1,
    default_args={
        "retries": 3,
        "retry_delay": timedelta(minutes=19),
    },
    tags=["model", "training"],
    doc_md="""
    ### Training & Archiving Pipeline
    Archeving old flight and weather files
    """,
)
def training_process():

    @task(task_id="launch_training")
    def launch_training():
        training_class = XGBGridSearch().training_model()
        return training_class

    archiving_files = BashOperator(
        task_id="archeving_files",
        bash_command="mv /opt/airflow/output/*.parquet /opt/airflow/archives",
    )

    training_results = launch_training()
    training_results >> archiving_files


training_process()
