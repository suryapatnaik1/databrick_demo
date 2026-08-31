# Databricks notebook source
dbutils.widgets.text("catalog", "sp_catalog")
dbutils.widgets.text("schema", "dab_orchestration_demo")

catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")

core_row_count = dbutils.jobs.taskValues.get(
    taskKey="create_core_table", key="core_row_count", default=None
)

print(f"Orchestration demo finished for {catalog}.{schema}. core_row_count={core_row_count}")
