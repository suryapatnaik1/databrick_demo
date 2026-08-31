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

### GitHub Actions

`.github/workflows/deploy.yml` runs `databricks bundle validate` on pull requests, and `deploy` + `run` on every push to `main`. Before it will work, add these repo secrets under **Settings → Secrets and variables → Actions**:

- `DATABRICKS_HOST` — your workspace URL
- `DATABRICKS_TOKEN` — a PAT from that workspace (User Settings → Developer → Access tokens)

Everything above targets a single `dev` environment for now. A `prod` target (a second entry in `databricks.yml` with `mode: production`, deployed on a tag or after manual approval) is a natural next step but isn't set up yet.