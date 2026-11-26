#!/usr/bin/env bash
set -Eeuo pipefail
IFS=$'\n\t'

: "${IMAGE_TAG:?IMAGE_TAG is required}"
: "${K3S_NODE_NAME:?K3S_NODE_NAME is required}"
: "${K3S_HOST_PATH:?K3S_HOST_PATH is required}"
: "${CI_COMMIT_BRANCH:?CI_COMMIT_BRANCH is required}"

readonly NAMESPACE="flight-project"

helm upgrade --install apis ./k3s/apis \
  --namespace "${NAMESPACE}" --create-namespace \
  -f k3s/apis/values.yaml \
  --set persistence.nodeName="${K3S_NODE_NAME}" \
  --set persistence.hostPath="${K3S_HOST_PATH}" \
  --set image.tag="${IMAGE_TAG}" \
  --atomic --timeout 5m

helm repo add apache-airflow https://airflow.apache.org
helm repo update

# Restrictions matérielles uniquement sur l'environnement de test
airflow_values=(-f k3s/airflow/values.yaml)
if [[ "${CI_COMMIT_BRANCH}" == "test_kube" ]]; then
  airflow_values+=(-f k3s/airflow/values-test.yaml)
fi

helm upgrade --install airflow apache-airflow/airflow \
  --version 1.22.0 \
  --namespace "${NAMESPACE}" \
  "${airflow_values[@]}" \
  --set images.airflow.tag="${IMAGE_TAG}" \
  --timeout 10m

# Monitoring
cp monitoring/grafana/provisioning/dashboards/fastapi.json k3s/monitoring/dashboards/fastapi.json
cp monitoring/grafana/provisioning/dashboards/airflow.json k3s/monitoring/dashboards/airflow.json

helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

helm upgrade --install monitoring prometheus-community/kube-prometheus-stack \
  --version "93.9.0" \
  --namespace monitoring --create-namespace \
  -f k3s/monitoring/values.yaml

kubectl create configmap grafana-dashboards \
  --from-file=fastapi.json=k3s/monitoring/dashboards/fastapi.json \
  --from-file=airflow.json=k3s/monitoring/dashboards/airflow.json \
  --namespace monitoring \
  --dry-run=client -o yaml | kubectl apply -f -
