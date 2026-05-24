from airflow.sdk import dag, task
from airflow.operators.python import get_current_context
from datetime import datetime, timedelta
from src.extract_data.get_datas import GetDatas

@dag(
    dag_id='ad_hoc_weather',
    description='A simple extract',
    schedule=None,
    catchup=False,
    max_active_runs=1,
    default_args={
        "retries": 3,
        "retry_delay": timedelta(minutes=5),
    },
    tags=['test', 'extract'],
    doc_md="""
    Extract weather one time, change date before in script
    Use api-prod to run this dag
    """
)

def Ad_Hoc():
    
    @task
    def extract_task(dag_run=None):
        if not dag_run or not dag_run.conf:
            raise AirflowFailException(
                "[WARNING] This DAG must be triggered via api-prod (8081). Manual execution without configuration is forbidden."
            )

        received_date = dag_run.conf.get("date_val")

        extractor = GetDatas(received_date).get_weather()
        return extractor

    extract_task()

Ad_Hoc()