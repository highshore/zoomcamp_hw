## Module 3 - Data Warehouse (BigQuery)

This folder contains my Homework 3 work for the Data Engineering Zoomcamp 2026.

### Setup

Create and activate the virtual environment used for this module:

```bash
python3 -m venv .venv_hw3
. .venv_hw3/bin/activate
python -m pip install --upgrade pip
python -m pip install google-cloud-storage google-cloud-bigquery requests
```

Set credentials and run the script:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/Users/nespresso/Downloads/zoomcamp-486915-7139a8a63c66.json"
export GCP_PROJECT_ID="zoomcamp-486915"
export GCP_BUCKET_NAME="zoomcamp_bucket_1"
export BQ_DATASET="ZoomCamp_BQ_Dataset"

python compute_hw3_answers.py
```

### Answers

1) Count of records for Yellow Taxi 2024 Jan–Jun: **20,332,093**  
2) Estimated bytes for distinct `PULocationID` (External vs Table): **0 MB** and **155.12 MB**  
3) Bytes are different because BigQuery is columnar and scans only requested columns.  
4) Records with `fare_amount = 0`: **8,333**  
5) Partition by `tpep_dropoff_datetime` and cluster by `VendorID`.  
6) Estimated bytes (non-partitioned vs partitioned): **310.24 MB** and **26.84 MB**  
7) External table data is stored in a GCS bucket.  
8) Best practice to always cluster data: **False**  
9) (Bonus) `SELECT count(*)` estimated bytes: **0 MB**
