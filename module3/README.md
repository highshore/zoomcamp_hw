## Module 3 - Data Warehouse (BigQuery)

This folder contains my Homework 3 work for Data Engineering Zoomcamp 2026.

## Objective

Load Yellow Taxi 2024 Jan-Jun data into GCS and BigQuery, then compute homework answers using table design and query-cost analysis.

## Concepts Used

- Cloud object storage ingestion (GCS)
- BigQuery external tables vs native tables
- Partitioning and clustering for scan reduction
- Dry runs to measure bytes processed
- End-to-end automation with Python clients (GCS + BigQuery)

## Course Concept Mapping (What and Where)

- Data warehouse architecture (Module 3 intro): raw files in GCS + analytical serving in BigQuery via `module3/compute_hw3_answers.py`.
- External tables vs native tables:
  - external: `create_external_table(...)`
  - native/materialized: `create_materialized_table(...)`.
- Partitioning and clustering best practices:
  - `PARTITION BY DATE(tpep_dropoff_datetime)`
  - `CLUSTER BY VendorID`
  in `create_partitioned_table(...)`.
- Query cost/performance analysis using bytes processed:
  - dry-run utility: `dry_run_bytes(...)`
  - applied in Q2/Q3/Q6/Q9 sections in `main()`.
- Pipeline automation and idempotence:
  - upload only when missing (`if not blob.exists()`)
  - dataset/table creation with `exists_ok=True`.

## File and What It Does

- `compute_hw3_answers.py`
  - Downloads monthly parquet files (Jan-Jun 2024)
  - Uploads them to GCS under `yellow/2024/`
  - Creates BigQuery dataset (if missing)
  - Creates external table over GCS files
  - Materializes external data into native table
  - Creates partitioned+clustered table
  - Executes homework queries and dry-runs
  - Prints JSON with all computed metrics

## Code Walkthrough

### Ingestion + Table Setup

1. `upload_parquet_files(...)`
   - Downloads each monthly parquet only if blob doesn’t already exist.
   - Uploads to `gs://<bucket>/yellow/2024/`.

2. `ensure_dataset(...)`
   - Creates dataset if needed in the same region as bucket.

3. `create_external_table(...)`
   - Defines BigQuery external table over `yellow_tripdata_2024-*.parquet`.

4. `create_materialized_table(...)`
   - Copies external table data into a native BigQuery table.

5. `create_partitioned_table(...)`
   - Creates table partitioned by `DATE(tpep_dropoff_datetime)`.
   - Clusters by `VendorID`.

### Answer Computation

- `run_query(...)` executes SQL and reads result values.
- `dry_run_bytes(...)` runs query in dry-run mode to get estimated processed bytes.

This is used to answer:

- row counts
- bytes scanned differences
- partitioned vs non-partitioned query cost

## Step-by-Step to Reproduce

Create environment and install dependencies:

```bash
python3 -m venv .venv_hw3
. .venv_hw3/bin/activate
python -m pip install --upgrade pip
python -m pip install google-cloud-storage google-cloud-bigquery requests
```

Set env vars:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your-service-account.json"
export GCP_PROJECT_ID="zoomcamp-486915"
export GCP_BUCKET_NAME="zoomcamp_bucket_1"
export BQ_DATASET="ZoomCamp_BQ_Dataset"
```

Run:

```bash
python compute_hw3_answers.py
```

## Answers

1. Count of records for Yellow Taxi 2024 Jan-Jun: **20,332,093**
2. Estimated bytes for distinct `PULocationID` (External vs Table): **0 MB** and **155.12 MB**
3. Bytes differ because BigQuery’s columnar storage scans only referenced columns.
4. Records with `fare_amount = 0`: **8,333**
5. Best strategy: partition by `tpep_dropoff_datetime` and cluster by `VendorID`.
6. Estimated bytes (non-partitioned vs partitioned): **310.24 MB** and **26.84 MB**
7. External table data location: **GCS bucket**
8. “Always cluster data” is best practice: **False**
9. Bonus `SELECT count(*)` estimated bytes: **0 MB**

## Why This Approach

- Re-runnable and automated end-to-end.
- Uses the same APIs used in production pipelines.
- Dry-run bytes provide objective cost/performance evidence.
