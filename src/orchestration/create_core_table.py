# Databricks notebook source
from pyspark.sql import Row

dbutils.widgets.text("catalog", "sp_catalog")
dbutils.widgets.text("schema", "dab_orchestration_demo")

catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")

df = spark.createDataFrame([
    Row(event_id=1, event_type="page_view"),
    Row(event_id=2, event_type="click"),
    Row(event_id=3, event_type="purchase"),
])
df.write.mode("overwrite").saveAsTable(f"{catalog}.{schema}.core_events")

# hand a value downstream to any task that depends on this one
dbutils.jobs.taskValues.set(key="core_row_count", value=df.count())
