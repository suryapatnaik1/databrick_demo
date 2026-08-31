# Databricks notebook source
from pyspark.sql import Row

dbutils.widgets.text("catalog", "sp_catalog")
dbutils.widgets.text("schema", "dab_orchestration_demo")

catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")

# read a value produced by an upstream task
core_row_count = dbutils.jobs.taskValues.get(
    taskKey="create_core_table", key="core_row_count", default=0
)

df = spark.createDataFrame([
    Row(flag="core_row_count", value=str(core_row_count)),
    Row(flag="enrichment_ready", value="true"),
])
df.write.mode("overwrite").saveAsTable(f"{catalog}.{schema}.enrichment_flags")
