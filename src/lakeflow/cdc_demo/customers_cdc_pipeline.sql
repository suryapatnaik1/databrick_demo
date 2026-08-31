CREATE OR REFRESH STREAMING TABLE bronze_customer_changes
AS SELECT * FROM STREAM read_files(
  '/Volumes/sp_catalog/dab_lakeflow_cdc_demo/raw_events',
  format => 'json'
);

CREATE OR REFRESH STREAMING TABLE customers_scd1;

CREATE FLOW customers_scd1_flow AS AUTO CDC INTO customers_scd1
FROM STREAM bronze_customer_changes
KEYS (customer_id)
APPLY AS DELETE WHEN operation = 'DELETE'
SEQUENCE BY sequence_num
STORED AS SCD TYPE 1;

CREATE OR REFRESH STREAMING TABLE customers_scd2;

CREATE FLOW customers_scd2_flow AS AUTO CDC INTO customers_scd2
FROM STREAM bronze_customer_changes
KEYS (customer_id)
APPLY AS DELETE WHEN operation = 'DELETE'
SEQUENCE BY sequence_num
STORED AS SCD TYPE 2;
