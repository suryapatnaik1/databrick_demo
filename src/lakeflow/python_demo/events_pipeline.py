import dlt
from pyspark.sql import Row
from pyspark.sql.functions import col


@dlt.table(comment="Raw web events (inline sample data)")
def bronze_events():
    return spark.createDataFrame([
        Row(event_id=1, user_id="u1", event_type="page_view", event_date="2026-08-01"),
        Row(event_id=2, user_id="u1", event_type="click", event_date="2026-08-01"),
        Row(event_id=3, user_id="u2", event_type="page_view", event_date="2026-08-02"),
        Row(event_id=4, user_id="u2", event_type="purchase", event_date="2026-08-02"),
        Row(event_id=5, user_id="u3", event_type="page_view", event_date=None),  # dropped downstream
    ])


@dlt.table(comment="Cleaned events; drops rows missing an event_date")
@dlt.expect_or_drop("valid_event_date", "event_date IS NOT NULL")
def silver_events():
    return dlt.read("bronze_events").withColumn("event_date", col("event_date").cast("date"))


@dlt.table(comment="Daily event counts by type")
def gold_daily_event_counts():
    return (
        dlt.read("silver_events")
        .groupBy("event_date", "event_type")
        .count()
        .withColumnRenamed("count", "event_count")
    )
