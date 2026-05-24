FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends ca-certificates openssl wget && \
    update-ca-certificates && \
    rm -rf /var/lib/apt/lists/*

RUN useradd -m apiuser

WORKDIR /app

COPY --chown=apiuser:apiuser pyproject.toml ./
COPY --chown=apiuser:apiuser src/ ./src/

COPY --chown=apiuser:apiuser ./api-prod/ .

RUN pip install ".[api]"

USER apiuser

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]