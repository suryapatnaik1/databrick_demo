# Databricks notebook source
dbutils.widgets.text("catalog", "sp_catalog")
dbutils.widgets.text("schema", "dab_orchestration_demo")

catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {catalog}.{schema}")
