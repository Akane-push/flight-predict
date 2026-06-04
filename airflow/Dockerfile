FROM apache/airflow:3.2.0-python3.11

USER airflow

RUN pip install polars

COPY --chown=airflow:root pyproject.toml ./
COPY --chown=airflow:root src/ /opt/airflow/src/
RUN pip install --no-cache-dir ".[airflow]"

COPY --chown=airflow:root ./airflow/dags/ /opt/airflow/dags/