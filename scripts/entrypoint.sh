#!/bin/sh
# Copy VaultSpeed DAG support files (mappings, variables JSON) to Airflow dags dir
# so generated DAGs using Variable.get("path_to_metadata") find them at runtime.
mkdir -p /usr/local/airflow/dags
cp -n /opt/airflow/dag_support/*.json /usr/local/airflow/dags/ 2>/dev/null || true
if [ -x /usr/local/bin/entrypoint ]; then
  exec /usr/local/bin/entrypoint "$@"
else
  exec "$@"
fi
