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

# Rest of project (dags, plugins, etc.)
COPY --chown=astro:0 . .
