r"""
 __     __          _ _                           _      __  ___  __   __   
 \ \   / /_ _ _   _| | |_ ___ ____   ___  ___  __| |     \ \/ _ \/ /  /_/   
  \ \ / / _` | | | | | __/ __|  _ \ / _ \/ _ \/ _` |      \/ / \ \/ /\      
   \ V / (_| | |_| | | |_\__ \ |_) |  __/  __/ (_| |      / / \/\ \/ /      
    \_/ \__,_|\__,_|_|\__|___/ .__/ \___|\___|\__,_|     /_/ \/_/\__/       
                             |_|                                            

Vaultspeed version: 6.0.0.5, generation date: 2026/03/12 23:06:29
Pipeline: double_CRM - Description: Run Twice - Version: 1.0.0 - Commit message:  - lock date: 2026/03/12 23:06:24
 """

from airflow import DAG
from airflow.models import Variable

from datetime import datetime, timedelta
from pathlib import Path
import json
import ast

from airflow.providers.standard.operators.empty import EmptyOperator
from vaultspeed_provider.operators.databricks_operator import VSDatabricksSubmitRunOperator


default_args = {
	"owner": "Vaultspeed"
}


path_to_mtd = Path(Variable.get("path_to_metadata"))


with open(path_to_mtd / "13_mappings_double_CRM_20260312_230629.json") as file: 
	mappings = json.load(file)


double_CRM = DAG(
	dag_id="double_CRM",
	default_args=default_args,
	description="Run Twice",
	schedule="@daily",
	start_date=datetime.fromisoformat("2026-03-12T20:00:15+01:00"),
	catchup=False,
	max_active_tasks=3
)

start_task = EmptyOperator(
	task_id="START",
	dag=double_CRM
)

tasks = {"START":start_task}

for comp, info in mappings.items():
	if info["component_type"] == "operator":

		task = EmptyOperator(
			task_id=comp,
			dag=double_CRM,
			trigger_rule=info["trigger_rule"]
		)

	elif info["component_type"] == "custom_task_comp":

		# Process custom_parameters: apply ast.literal_eval() on values, then resolve callables
		custom_params = {}
		for key, value in info.get("custom_parameters", {}).items():
			if isinstance(value, str):
				# First try ast.literal_eval() for literals (booleans, numbers, lists, dicts, etc.)
				try:
					value = ast.literal_eval(value)
				except (ValueError, SyntaxError):
					# If literal_eval fails, try to resolve as callable from globals
					if value in globals():
						obj = globals()[value]
						if callable(obj):
							value = obj
					# Otherwise keep as string
			custom_params[key] = value
	                             
		task = globals()[info["airflow_operator"]](
			task_id=comp,
			dag=double_CRM,
			trigger_rule=info["trigger_rule"],
			**custom_params
		)

	else:

		task = VSDatabricksSubmitRunOperator(
		task_id=comp,
		databricks_conn_id="mloz",
		notebook_task={
			"notebook_path": f"""{{{{var.value.databricks_path}}}}FLOW_STUDIO_MAPPINGS/Domains/CRM/{info["original_name"]}{{{{var.value.databricks_file_extension}}}}"""
		},
		existing_cluster_id="{{ conn.mloz.extra_dejson.get('cluster_id') }}",
			trigger_rule=info["trigger_rule"],
		dag=double_CRM
)


	tasks[comp] = task


# Set up dependencies in a second pass
for comp, info in mappings.items():
	for dep in info["dependencies"]:
		tasks[comp] << tasks[dep]


