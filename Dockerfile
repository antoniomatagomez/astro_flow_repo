# Use the -base image so we control COPY order (zip must exist before pip install).
FROM astrocrpublic.azurecr.io/runtime:3.1-13-base

USER root

# System packages
COPY packages.txt .
RUN /usr/local/bin/install-system-packages

# Python deps: copy requirements AND the zip so "pip install ./vs_fmc_plugin.zip[all]" works
COPY requirements.txt .
COPY vs_fmc_plugin.zip .
RUN /usr/local/bin/install-python-dependencies

USER astro

# Rest of project (dags with all .py and .json, plugins, etc.)
COPY --chown=astro:0 . .

# VaultSpeed: store DAG support JSON in a fixed path so entrypoint can copy to
# /usr/local/airflow/dags at startup (original generated DAGs use path_to_metadata)
USER root
RUN mkdir -p /usr/local/airflow/dags /opt/airflow/dag_support && ( [ -d dags ] && cp -rn dags/. /usr/local/airflow/dags/ && cp -n dags/*.json /opt/airflow/dag_support/ 2>/dev/null ; true )

# Entrypoint: copy dag_support JSON to /usr/local/airflow/dags so generated DAGs find them
COPY scripts/entrypoint.sh /opt/airflow/scripts/entrypoint.sh
RUN chmod +x /opt/airflow/scripts/entrypoint.sh && chown -R astro:0 /opt/airflow/dag_support /opt/airflow/scripts
ENTRYPOINT ["/opt/airflow/scripts/entrypoint.sh"]

USER astro
