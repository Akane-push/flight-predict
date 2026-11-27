#!/usr/bin/env bash
set -Eeuo pipefail

readonly ZERO_SHA="0000000000000000000000000000000000000000"

if [[ -n "${CI_MERGE_REQUEST_DIFF_BASE_SHA:-}" ]]; then
  log_opts="${CI_MERGE_REQUEST_DIFF_BASE_SHA}..${CI_COMMIT_SHA}"
elif [[ -z "${CI_COMMIT_BEFORE_SHA:-}" || "${CI_COMMIT_BEFORE_SHA}" == "${ZERO_SHA}" ]]; then
  log_opts="--all"
else
  log_opts="${CI_COMMIT_BEFORE_SHA}..${CI_COMMIT_SHA}"
fi

gitleaks git --redact --verbose --log-opts="${log_opts}" \
  --report-format=sarif --report-path=gitleaks-report.sarif .
