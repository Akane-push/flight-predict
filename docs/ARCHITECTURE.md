# Architecture — flight-predict

```mermaid
flowchart TB
    subgraph EXT["Sources externes"]
        LUFTH["API Lufthansa"]
        CLIENT["Client / Utilisateur"]
    end

    subgraph CI["CI/CD — GitLab"]
        GITCI["Pipeline .gitlab-ci.yml<br/>security → build → test → deploy"]
        REG["Registry GitLab<br/>(images Docker)"]
    end

    subgraph K3S["Cluster K3s — namespace flight-project"]
        subgraph AIRFLOW["Airflow 3.2 (CeleryExecutor)"]
            SCHED["Scheduler"]
            WORKER["Worker(s)"]
            DAGPROC["Dag Processor"]
            TRIG["Triggerer"]
            AFAPI["Airflow API Server"]
        end

        subgraph APIS["APIs FastAPI"]
            APIPROD["api-prod :8081<br/>déclenche les DAGs"]
            APIPREDICT["api-predict :8001<br/>prédictions + aéroports"]
        end

        PG[("PostgreSQL")]
        REDIS[("Redis — broker Celery")]
        PVC[("PVC data-pvc<br/>local-storage")]

        subgraph MON["Monitoring"]
            STATSD["StatsD Exporter"]
            PROM["Prometheus"]
            GRAF["Grafana<br/>dashboards Airflow + FastAPI"]
        end
    end

    %% Flux CI/CD
    GITCI -->|build & push| REG
    REG -->|helm upgrade| AIRFLOW
    REG -->|helm upgrade| APIS

    %% Flux data / métier
    LUFTH -->|extraction vols/météo| DAGPROC
    DAGPROC --> SCHED
    SCHED --> WORKER
    WORKER --> PG
    WORKER --> PVC
    CLIENT -->|requêtes| APIPREDICT
    APIPROD -->|trigger DAG via token| AFAPI
    AFAPI --> SCHED
    SCHED --> REDIS
    WORKER --> REDIS

    %% Monitoring
    AIRFLOW -.->|metrics| STATSD
    APIS -.->|metrics /metrics| PROM
    STATSD --> PROM
    PROM --> GRAF

    classDef ext fill:#f4f4f4,stroke:#999
    classDef ci fill:#e8f0fe,stroke:#4285f4
    classDef mon fill:#fef7e0,stroke:#f9ab00
    class EXT,LUFTH,CLIENT ext
    class CI,GITCI,REG ci
    class MON,STATSD,PROM,GRAF mon

flowchart TD

subgraph group_collection["Data collection"]
  node_get_datas["Data collection tasks<br/>[get_datas.py]"]
  node_flight_extract["Flight extraction<br/>[flight_data.py]"]
  node_weather_extract["Weather extraction<br/>[weather_data.py]"]
  node_lufthansa_auth["Lufthansa auth<br/>[identification.py]"]
  node_parquet_store[("Parquet data")]
end

subgraph group_processing["Preparation and training"]
  node_cleaning["Data cleaning<br/>[data_cleaning.py]"]
  node_trainer["Model training"]
  node_model_store[("Model files")]
end

subgraph group_orchestration["Airflow orchestration"]
  node_airflow_api["Airflow API"]
  node_flight_dag["Flight DAGs"]
  node_weather_dag["Weather DAGs"]
  node_adhoc_flight_dag["Ad-hoc flight DAG"]
  node_adhoc_weather_dag["Ad-hoc weather DAG"]
  node_training_dag["Training DAG<br/>[training_model.py]"]
end

subgraph group_services["API services"]
  node_prod_api["Production API<br/>[main.py]"]
  node_predict_api["Prediction API<br/>[main.py]"]
  node_validation["Date validation<br/>[exception.py]"]
  node_api_auth["API key auth<br/>[api_key_auth.py]"]
  node_rate_limiter["Rate limiting"]
  node_airport_refs[("Airport references")]
end

node_user(("API user"))
node_lufthansa["Lufthansa API"]
node_openmeteo["Open-Meteo"]

node_user -->|"requests"| node_prod_api
node_user -->|"requests"| node_predict_api
node_prod_api -->|"validates dates"| node_validation
node_prod_api -->|"limits requests"| node_rate_limiter
node_predict_api -->|"verifies key"| node_api_auth
node_predict_api -->|"limits requests"| node_rate_limiter
node_predict_api -->|"reads airports"| node_airport_refs
node_prod_api -->|"triggers DAGs"| node_airflow_api
node_airflow_api -.->|"dispatches"| node_adhoc_flight_dag
node_airflow_api -.->|"dispatches"| node_adhoc_weather_dag
node_flight_dag -->|"invokes tasks"| node_get_datas
node_weather_dag -->|"invokes tasks"| node_get_datas
node_adhoc_flight_dag -->|"invokes tasks"| node_get_datas
node_adhoc_weather_dag -->|"invokes tasks"| node_get_datas
node_training_dag -->|"invokes training"| node_trainer
node_get_datas -->|"calls extractor"| node_flight_extract
node_get_datas -->|"calls extractor"| node_weather_extract
node_get_datas -->|"cleans scheduled data"| node_cleaning
node_flight_extract -->|"gets token"| node_lufthansa_auth
node_lufthansa_auth -->|"requests token"| node_lufthansa
node_flight_extract -->|"fetches flights"| node_lufthansa
node_weather_extract -->|"fetches weather"| node_openmeteo
node_get_datas -->|"writes extracts"| node_parquet_store
node_weather_extract -->|"reads flights"| node_parquet_store
node_trainer -->|"reads extracts"| node_parquet_store
node_trainer -->|"cleans training data"| node_cleaning
node_trainer -->|"saves model"| node_model_store



    classDef toneNeutral fill:#f8fafc,stroke:#334155,stroke-width:1.5px,color:#0f172a
    classDef toneBlue fill:#dbeafe,stroke:#2563eb,stroke-width:1.5px,color:#172554
    classDef toneAmber fill:#fef3c7,stroke:#d97706,stroke-width:1.5px,color:#78350f
    classDef toneMint fill:#dcfce7,stroke:#16a34a,stroke-width:1.5px,color:#14532d
    classDef toneRose fill:#ffe4e6,stroke:#e11d48,stroke-width:1.5px,color:#881337
    classDef toneIndigo fill:#e0e7ff,stroke:#4f46e5,stroke-width:1.5px,color:#312e81
    classDef toneTeal fill:#ccfbf1,stroke:#0f766e,stroke-width:1.5px,color:#134e4a
    class node_get_datas,node_flight_extract,node_weather_extract,node_lufthansa_auth,node_parquet_store,node_user toneBlue
    class node_cleaning,node_trainer,node_model_store toneAmber
    class node_airflow_api,node_flight_dag,node_weather_dag,node_adhoc_flight_dag,node_adhoc_weather_dag,node_training_dag,node_lufthansa toneMint
    class node_prod_api,node_predict_api,node_validation,node_api_auth,node_rate_limiter,node_airport_refs toneRose
    class node_openmeteo toneIndigo
```

## Lecture du schéma

- **CI/CD**: chaque push déclenche le pipeline GitLab, qui build les images Docker et les pousse vers le registry. Un `helm upgrade` déploie ensuite sur le cluster K3s.
- **Flux métier**: les DAGs Airflow extraient les données (vols via l'API Lufthansa, météo) et alimentent la base de donnée et le stockage persistant. `api-prod` sert de point d'entrée pour déclencher des DAGs à la demande ; `api-predict` expose les prédictions aux clients.
- **Monitoring**: Airflow et les APIs exposent des métriques (StatsD / endpoint `/metrics`), collectées par Prometheus et visualisées dans Grafana.
- **Infra sous-jacente** (non représentée ici, voir le projet [terraform-flight-predict](https://github.com/Akane-push/terraform-flight-predict)): le cluster K3s tourne sur des VMs OVH provisionnées par Terraform et configurées par Ansible.
