# Databricks notebook source
from pyspark.sql import Row

dbutils.widgets.text("catalog", "sp_catalog")
dbutils.widgets.text("schema", "dab_orchestration_demo")
dbutils.widgets.text("region", "us")

catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")
region = dbutils.widgets.get("region")

df = spark.createDataFrame([
    Row(region=region, sales=100),
    Row(region=region, sales=250),
])
df.write.mode("overwrite").saveAsTable(f"{catalog}.{schema}.sales_{region}")
