# databrick_demo

## Deploying with Databricks Asset Bundles

This repo includes a minimal [Databricks Asset Bundle](https://docs.databricks.com/en/dev-tools/bundles/index.html) (`databricks.yml`, `resources/hello_dab_job.yml`, `src/hello_dab.py`) defining one job, `hello_dab_job`, that creates a small DataFrame and writes it to `sp_catalog.dab_demo.hello_dab`. It exists to demonstrate the DAB deploy workflow, separate from the exploratory notebooks in this repo.

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

### GitHub Actions

`.github/workflows/deploy.yml` runs `databricks bundle validate` on pull requests, and `deploy` + `run` on every push to `main`. Before it will work, add these repo secrets under **Settings → Secrets and variables → Actions**:

- `DATABRICKS_HOST` — your workspace URL
- `DATABRICKS_TOKEN` — a PAT from that workspace (User Settings → Developer → Access tokens)

Everything above targets a single `dev` environment for now. A `prod` target (a second entry in `databricks.yml` with `mode: production`, deployed on a tag or after manual approval) is a natural next step but isn't set up yet.