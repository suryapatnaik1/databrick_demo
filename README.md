# databrick_demo

Two things live here: ad-hoc notebooks exploring Unity Catalog/Delta/Iceberg (`Day 1 - Create catalog.ipynb`, `Day 2 - Create delta tables.ipynb`, `Day 2 - Execute notebook.ipynb`), and a [Databricks Asset Bundle](https://docs.databricks.com/en/dev-tools/bundles/index.html) built up incrementally to learn DAB deploy mechanics and Databricks Workflows/Lakeflow orchestration. The bundle is deployed via GitHub Actions on every push to `main`; nothing runs automatically — every job/pipeline below is triggered by hand so you can see what each one does.

### Resources at a glance

| Resource | Type | What it shows |
|---|---|---|
| `hello_dab_job` | Job | Minimal single-task job — the basic deploy workflow |
| `orchestration_demo_job` | Job | Multi-task DAG: `condition_task` branching, job parameters, `for_each_task`, cross-task values, retries, `run_if`, `run_job_task` |
| `lakeflow_sql_demo` | Pipeline (SQL) | Declarative bronze → silver → gold with a `CONSTRAINT ... EXPECT` data-quality rule |
| `lakeflow_python_demo` | Pipeline (Python) | Same shape via `@dlt.table` / `@dlt.expect_or_drop` |
| `seed_cdc_events_job` + `lakeflow_cdc_demo` | Job + Pipeline | Autoloader (`STREAM read_files`) feeding two `AUTO CDC INTO` flows — SCD Type 1 vs Type 2 |

## Deploying with Databricks Asset Bundles

`databricks.yml`, `resources/hello_dab_job.yml`, `src/hello_dab.py` define the first and simplest job, `hello_dab_job`, which creates a small DataFrame and writes it to `sp_catalog.dab_demo.hello_dab`.

### Local setup

Install the CLI:

```bash
curl -fsSL https://raw.githubusercontent.com/databricks/setup-cli/main/install.sh | sh
# or: brew tap databricks/tap && brew install databricks
```

Authenticate (either export `DATABRICKS_HOST`/`DATABRICKS_TOKEN`, or run `databricks configure`), then:

```bash
databricks bundle validate -t dev
databricks bundle deploy -t dev
databricks bundle run hello_dab_job -t dev
```

The identity you authenticate as needs `USE CATALOG` on `sp_catalog` and `CREATE SCHEMA` privileges (same grants used in `Day 1 - Create catalog.ipynb`).

### Orchestration demo job

`resources/orchestration_demo_job.yml` (tasks in `src/orchestration/`) is a second job, `orchestration_demo_job`, built to exercise Databricks Workflows' orchestration features rather than to do anything with the data: a multi-task DAG (`depends_on`), a `condition_task` branch driven by a job parameter, job parameters flowing into per-task `base_parameters`, cross-task data passing (`dbutils.jobs.taskValues`), a `for_each_task` loop over a list parameter, a `run_job_task` that calls `hello_dab_job` as a sub-job, retry/timeout policy, `run_if: ALL_DONE` outcome handling, a paused cron `schedule`, and `email_notifications`. It writes to `sp_catalog.dab_orchestration_demo`, kept separate from `dab_demo`.

CI deploys this job on every push to `main` (it's included automatically via `resources/*.yml`) but does **not** run it — trigger runs yourself while exploring:

```bash
databricks bundle deploy -t dev
databricks bundle run orchestration_demo_job -t dev
databricks bundle run orchestration_demo_job -t dev --params run_mode=quick   # skips create_optional_table
```

### Lakeflow pipeline samples

Two [Lakeflow Declarative Pipelines](https://docs.databricks.com/en/delta-live-tables/index.html) (formerly Delta Live Tables) show the other Databricks resource type: instead of task-by-task orchestration, you declare tables and Databricks resolves the dependency graph and refresh order itself.

- **`lakeflow_sql_demo`** (`resources/lakeflow_sql_demo.yml`, `src/lakeflow/sql_demo/orders_pipeline.sql`) — SQL-authored: `bronze_orders` → `silver_orders` → `gold_sales_by_product`. `silver_orders` declares `CONSTRAINT valid_quantity EXPECT (quantity > 0) ON VIOLATION DROP ROW`, a declarative data-quality rule — one seeded row has a negative quantity specifically to show it get dropped rather than failing the pipeline. Writes to `sp_catalog.dab_lakeflow_sql_demo`.
- **`lakeflow_python_demo`** (`resources/lakeflow_python_demo.yml`, `src/lakeflow/python_demo/events_pipeline.py`) — Python-authored with the `dlt` decorator API: `bronze_events` → `silver_events` → `gold_daily_event_counts`. `silver_events` uses `@dlt.expect_or_drop`, the Python equivalent of the SQL constraint above. Writes to `sp_catalog.dab_lakeflow_python_demo`.

Both use `MATERIALIZED VIEW`/`@dlt.table` over inline literal data (batch, not streaming tables) since there's no incremental source here — the Autoloader-fed streaming table below is the incremental counterpart to these. Both run on serverless compute and are triggered, not continuous — deployed by CI like the jobs above, but not auto-run:

```bash
databricks bundle deploy -t dev
databricks bundle run lakeflow_sql_demo -t dev
databricks bundle run lakeflow_python_demo -t dev
```

### Autoloader + SCD (AUTO CDC) sample

Two more resources, together demonstrating incremental file ingestion and slowly changing dimensions — features that need actual multi-batch data to be worth seeing, unlike the samples above:

- **`seed_cdc_events_job`** (`resources/seed_cdc_events_job.yml`, `src/lakeflow/cdc_demo/seed_customer_events.py`) — a job, parameterized by `batch`, that creates a Unity Catalog Volume (`sp_catalog.dab_lakeflow_cdc_demo.raw_events`) and writes one JSON file of hardcoded "customer change event" records into it per batch: `batch=1` is an initial load (3 inserts), `batch=2` is a set of changes (an update, a delete, a new insert).
- **`lakeflow_cdc_demo`** (`resources/lakeflow_cdc_demo.yml`, `src/lakeflow/cdc_demo/customers_cdc_pipeline.sql`) — a pipeline where `bronze_customer_changes` is a **streaming table** built from `STREAM read_files(...)` (this is Autoloader: it incrementally picks up whatever files exist in the volume), feeding two `AUTO CDC INTO` flows off the same stream — `customers_scd1` (`STORED AS SCD TYPE 1`, upserts/deletes in place) and `customers_scd2` (`STORED AS SCD TYPE 2`, keeps every version via `__START_AT`/`__END_AT`).

This one only makes sense run twice — seed a batch, run the pipeline, seed the next batch, run the pipeline again:

```bash
databricks bundle deploy -t dev
databricks bundle run seed_cdc_events_job -t dev --params batch=1
databricks bundle run lakeflow_cdc_demo -t dev
databricks bundle run seed_cdc_events_job -t dev --params batch=2
databricks bundle run lakeflow_cdc_demo -t dev
```

After both runs, compare `sp_catalog.dab_lakeflow_cdc_demo.customers_scd1` (3 current rows, Bob gone entirely) against `customers_scd2` (5 rows — Alice's and Bob's old rows still present with `__END_AT` set) to see the difference between the two SCD types.

### GitHub Actions

`.github/workflows/deploy.yml` runs `databricks bundle validate` on pull requests, and `databricks bundle deploy -t dev` on every push to `main` — it deploys every job and pipeline in the bundle but doesn't run any of them; trigger runs yourself (see the `databricks bundle run ...` commands above). Before deploy will work, add these repo secrets under **Settings → Secrets and variables → Actions**:

- `DATABRICKS_HOST` — your workspace URL
- `DATABRICKS_TOKEN` — a PAT from that workspace (User Settings → Developer → Access tokens)

Everything above targets a single `dev` environment for now. A `prod` target (a second entry in `databricks.yml` with `mode: production`, deployed on a tag or after manual approval) is a natural next step but isn't set up yet.