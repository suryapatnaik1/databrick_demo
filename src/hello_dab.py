# Databricks notebook source
from pyspark.sql import Row

spark.sql("CREATE SCHEMA IF NOT EXISTS sp_catalog.dab_demo")

df = spark.createDataFrame([
    Row(id=1, message="hello from a Databricks Asset Bundle"),
    Row(id=2, message="deployed via GitHub Actions"),
])

df.write.mode("overwrite").saveAsTable("sp_catalog.dab_demo.hello_dab")

display(spark.table("sp_catalog.dab_demo.hello_dab"))
