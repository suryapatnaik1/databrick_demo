# Databricks notebook source
import json

dbutils.widgets.text("catalog", "sp_catalog")
dbutils.widgets.text("schema", "dab_lakeflow_cdc_demo")
dbutils.widgets.text("batch", "1")

catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")
batch = dbutils.widgets.get("batch")

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {catalog}.{schema}")
spark.sql(f"CREATE VOLUME IF NOT EXISTS {catalog}.{schema}.raw_events")

volume_path = f"/Volumes/{catalog}/{schema}/raw_events"

# each batch simulates a new drop of customer change events landing in storage
batches = {
    "1": [  # initial load
        {"customer_id": 1, "name": "Alice", "city": "London", "operation": "INSERT", "sequence_num": 100},
        {"customer_id": 2, "name": "Bob", "city": "Paris", "operation": "INSERT", "sequence_num": 100},
        {"customer_id": 3, "name": "Cara", "city": "Berlin", "operation": "INSERT", "sequence_num": 100},
    ],
    "2": [  # Alice moves, Bob is removed, Dana is new
        {"customer_id": 1, "name": "Alice", "city": "Manchester", "operation": "UPDATE", "sequence_num": 200},
        {"customer_id": 2, "name": "Bob", "city": "Paris", "operation": "DELETE", "sequence_num": 200},
        {"customer_id": 4, "name": "Dana", "city": "Madrid", "operation": "INSERT", "sequence_num": 200},
    ],
}

records = batches.get(batch)
if records is None:
    raise ValueError(f"Unknown batch '{batch}', expected one of {list(batches)}")

file_path = f"{volume_path}/batch_{batch}.json"
content = "\n".join(json.dumps(r) for r in records)
dbutils.fs.put(file_path, content, overwrite=True)

print(f"Wrote {len(records)} records to {file_path}")
