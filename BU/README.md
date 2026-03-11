# Astro image with VaultSpeed plugin (Flow_Studio)

This project builds the **Astronomer Astro** (Airflow) image for the **Flow_Studio** deployment. It includes the **VaultSpeed FMC Airflow provider** and the dependencies your DAGs need.

## Contents

- **Dockerfile** – Uses `astrocrpublic.azurecr.io/astronomer/astro-runtime:3.1-13` (base image), installs system packages from `packages.txt`, then Python deps from `requirements.txt` (including the VaultSpeed plugin from `vs_fmc_plugin.zip`).
- **requirements.txt** – Installs `./vs_fmc_plugin.zip[all]` plus provider deps (Snowflake, Databricks, JDBC, etc.).
- **packages.txt** – Optional system packages (empty if none needed).
- **vs_fmc_plugin.zip** – VaultSpeed Airflow provider; keep this in the project root for the build.
- **dags/** – Place your Airflow DAGs here.

## Build the image

From this directory:

```bash
docker build -t astro-vaultspeed:latest .
```

## Deploy to Flow_Studio

With the [Astro CLI](https://docs.astronomer.io/astro/cli/install-cli):

```bash
astro deploy
```

Select or create the **Flow_Studio** deployment when prompted.

For local development:

```bash
astro dev start
```

## VaultSpeed provider

The provider is installed from `vs_fmc_plugin.zip` via `requirements.txt` with the `[all]` extra (JDBC, Snowflake, Google, Databricks). It adds operators, hooks, and sensors used by VaultSpeed Flow Management Control (FMC). Docs: [VaultSpeed – Defining a Flow](https://docs.vaultspeed.com/space/VPD/3013672989/Defining+a+Flow).
