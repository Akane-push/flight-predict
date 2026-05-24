FROM apache/airflow:3.2.0-python3.11

USER airflow

COPY --chmod=755 --chown=airflow:0 ./install_polars.sh .
RUN ./install_polars.sh

COPY pyproject.toml ./
COPY src/ ./src/
RUN pip install ".[airflow]"