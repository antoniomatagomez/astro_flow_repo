# Astro image with VaultSpeed plugin (Flow_Studio)

This project builds the **Astronomer Astro** (Airflow) image for the **Flow_Studio** deployment. It includes the **VaultSpeed FMC Airflow provider** and the dependencies your DAGs need.

## Contents

- **Dockerfile** – Uses `astrocrpublic.azurecr.io/astronomer/astro-runtime:3.1-13` (base image), installs system packages from `packages.txt`, then Python deps from `requirements.txt` (including the VaultSpeed plugin from `vs_fmc_plugin.zip`).
- **requirements.txt** – Installs `./vs_fmc_plugin.zip[all]` plus provider deps (Snowflake, Databricks, JDBC, etc.).
- **packages.txt** – Optional system packages (empty if none needed).
- **vs_fmc_plugin.zip** – VaultSpeed Airflow provider; keep this in the project root for the build.
- **dags/** – Place your Airflow DAGs here. Include both the VaultSpeed-generated `.py` DAGs and their `.json` (mappings, variables) in the same folder.
- **scripts/entrypoint.sh** – On container startup, copies DAG support JSON from `/opt/airflow/dag_support/` to `/usr/local/airflow/dags/` so **VaultSpeed-generated DAGs** (which use `Variable.get("path_to_metadata")`) find the files without editing the generated Python.

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

### DAG-only deploy and JSON files (`astro deploy -n Flow_Studio --dags -f`)

To have **both** Python DAGs and their JSON (mappings, variables) deployed when you run:

```bash
astro deploy -n Flow_Studio --dags -f
```

do the following:

1. **Keep all support files in `dags/`**  
   Put every VaultSpeed-generated `.py` and its `.json` files (mappings, variables) in the same `dags/` folder. The Astro CLI bundles the **entire** `dags/` directory for `--dags` deploys, so `.json` files are included as long as they are in `dags/`.

2. **Don’t exclude them**  
   - Leave `dags/.airflowignore` empty or ensure it does **not** list your `.json` files (`.airflowignore` controls which files Airflow parses as DAGs; it should not remove JSON from the folder).  
   - Don’t add `dags/` or `dags/*.json` to `.dockerignore` if you rely on a full image build to ship JSON; for `--dags` deploys the CLI reads from the local `dags/` folder, not the Docker context.

3. **Verify the bundle (optional)**  
   From the project root, see what would be in the bundle:
   ```bash
   tar -czf /tmp/dags-bundle-test.tar.gz -C dags . && tar -tzf /tmp/dags-bundle-test.tar.gz
   ```
   You should see your `.py` and `.json` files listed.

4. **If JSON still don’t appear at runtime**  
   Do a **full deploy** once (no `--dags`): `astro deploy -n Flow_Studio -f`. That builds the image with the entrypoint and with JSON in `/opt/airflow/dag_support/`. On every pod start, the entrypoint copies those into `/usr/local/airflow/dags/`, so even after later `--dags` deploys the runtime will have the JSON. Use `--dags` for quick DAG (.py) updates; use a full deploy when you add or change JSON or when you change the image (Dockerfile, requirements, etc.).

For local development:

```bash
astro dev start
```

## Databricks connection (cluster details)

DAGs that use `VSDatabricksSubmitRunOperator` (e.g. with `databricks_conn_id="mloz"`) need a Databricks connection with the **cluster ID in Extra**.

**In the Airflow UI** (Admin → Connections → Add / Edit):

| Field        | Value |
|-------------|--------|
| **Connection Id** | `mloz` (or the `databricks_conn_id` used in the DAG) |
| **Connection Type** | `Databricks` |
| **Host**     | Your workspace URL, e.g. `https://adb-1234567890123456.7.azuredatabricks.net` or `https://your-workspace.cloud.databricks.com` |
| **Login**    | `token` (or leave empty when using PAT in Password) |
| **Password** | Your Databricks [Personal Access Token](https://docs.databricks.com/en/dev-tools/auth/pat.html) |
| **Extra**   | JSON with the cluster ID: `{"cluster_id": "0123-456789-abcdef"}` |

Get the cluster ID from the Databricks UI: **Compute** → your cluster → **Configuration** tab, or from the cluster URL (e.g. `.../#setting/clusters/0123-456789-abcdef/...`).

**Local dev** only: you can define the same connection in `airflow_settings.yaml` (see the commented `mloz` example there).

## VaultSpeed-generated DAGs (no Python changes)

Generated DAGs use `Variable.get("path_to_metadata")` (e.g. `/usr/local/airflow/dags`) and expect mappings/variables JSON there. The image keeps that working without modifying generated code:

1. **Build time:** JSON files from `dags/*.json` are copied into `/opt/airflow/dag_support/` in the image.
2. **Startup:** `scripts/entrypoint.sh` runs before Airflow and copies `/opt/airflow/dag_support/*.json` into `/usr/local/airflow/dags/`.

Keep the Airflow Variable `path_to_metadata` set to `/usr/local/airflow/dags`. You can re-generate DAGs from VaultSpeed and redeploy without changing any Python.

## VaultSpeed provider

The provider is installed from `vs_fmc_plugin.zip` via `requirements.txt` with the `[all]` extra (JDBC, Snowflake, Google, Databricks). It adds operators, hooks, and sensors used by VaultSpeed Flow Management Control (FMC). Docs: [VaultSpeed – Defining a Flow](https://docs.vaultspeed.com/space/VPD/3013672989/Defining+a+Flow).
