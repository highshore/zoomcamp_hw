## Module 5 - Data Platforms (Bruin)

This folder contains my Homework 5 work for Data Engineering Zoomcamp 2026.

## Objective

Understand and apply Bruin data platform concepts (project structure, materialization, variables, dependency execution, quality checks, lineage, and full refresh behavior), then answer the Module 5 homework questions.

## Concepts Used

- Data platform abstractions: `pipeline`, `asset`, `environment`, `connection`
- Bruin project structure and required files
- Incremental/time-based materialization strategy selection
- Pipeline variable overrides via CLI
- Dependency-aware execution with downstream selection
- Built-in data quality checks (`not_null`)
- Lineage inspection and full refresh execution

## Course Concept Mapping (What and Where)

- Required project structure (Module 5 setup/tutorial): validated against Bruin Zoomcamp template structure (`.bruin.yml`, `pipeline/pipeline.yml`, `pipeline/assets/`).
- Materialization strategy for time-partitioned trip processing: applied conceptually as `time_interval` for month-based incremental rebuilds.
- Pipeline variables and runtime overrides:
  - variable schema in `pipeline.yml` (array of taxi types)
  - runtime override via `bruin run --var ...`.
- Dependency-aware execution:
  - running an updated asset and all descendants with `--downstream`.
- Data quality checks:
  - null-protection through `not_null` check on key columns like `pickup_datetime`.
- Metadata/lineage:
  - asset dependency visualization with `bruin lineage`.
- Fresh rebuild behavior:
  - force full table rebuild using `--full-refresh`.

## Files and What They Do

- `verify_hw5_cli.sh`
  - Validates key Bruin CLI options used in the homework answers from local `bruin --help` output.
  - Checks evidence for:
    - `bruin run --downstream`
    - `bruin run --var`
    - `bruin run --full-refresh`
    - `bruin lineage`

## How I Derived the Answers (Step-by-Step)

1. Read the official module homework in `cohorts/2026/05-data-platforms/homework.md`.
2. Cross-checked structure and commands against:
   - module tutorial docs in `05-data-platforms/README.md`
   - official Bruin Zoomcamp template README.
3. Verified CLI behavior locally with:
   - `bruin run --help`
   - `bruin lineage --help`
4. Mapped each multiple-choice option to documented/verified behavior and selected the exact match.

## Step-by-Step to Reproduce Validation

Install Bruin CLI:

```bash
curl -LsSf https://getbruin.com/install/cli | sh
```

Run validation script:

```bash
cd module5
bash verify_hw5_cli.sh
```

## Answers

1. Required Bruin files/directories: **`.bruin.yml` and `pipeline/` with `pipeline.yml` and `assets/`**
2. Best staging materialization for month-based processing: **`time_interval`**
3. Override `taxi_types` to only yellow: **`bruin run --var 'taxi_types=["yellow"]'`**
4. Run changed `ingestion/trips.py` plus downstream assets: **`bruin run ingestion/trips.py --downstream`**
5. Ensure `pickup_datetime` is never null: **`not_null: true`**
6. Visualize asset dependency graph: **`bruin lineage`**
7. First-time clean rebuild on new DB: **`--full-refresh`**

## Why This Approach

- Uses official course/template material plus local CLI verification.
- Keeps answers traceable to concrete command behavior.
- Matches the same reproducible and documented style used in modules 1-4.
