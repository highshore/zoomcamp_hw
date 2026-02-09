import json
import os
import tempfile
from typing import Any

import requests
from google.cloud import bigquery
from google.cloud import storage


PROJECT_ID = os.getenv("GCP_PROJECT_ID", "zoomcamp-486915")
BUCKET_NAME = os.getenv("GCP_BUCKET_NAME", "zoomcamp_bucket_1")
DATASET_ID = os.getenv("BQ_DATASET", "ZoomCamp_BQ_Dataset")

BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-{month}.parquet"
MONTHS = ["01", "02", "03", "04", "05", "06"]

GCS_PREFIX = "yellow/2024"
EXTERNAL_TABLE_ID = "yellow_tripdata_2024_ext"
MATERIALIZED_TABLE_ID = "yellow_tripdata_2024"
PARTITIONED_TABLE_ID = "yellow_tripdata_2024_partitioned"


def download_to_temp(url: str) -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".parquet") as tmp:
        with requests.get(url, stream=True, timeout=60) as resp:
            resp.raise_for_status()
            for chunk in resp.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    tmp.write(chunk)
        return tmp.name


def upload_parquet_files(storage_client: storage.Client) -> list[str]:
    bucket = storage_client.get_bucket(BUCKET_NAME)
    uploaded_uris = []
    for month in MONTHS:
        file_name = f"yellow_tripdata_2024-{month}.parquet"
        blob_path = f"{GCS_PREFIX}/{file_name}"
        blob = bucket.blob(blob_path)
        if not blob.exists():
            url = BASE_URL.format(month=month)
            temp_path = download_to_temp(url)
            blob.upload_from_filename(temp_path)
            os.unlink(temp_path)
        uploaded_uris.append(f"gs://{BUCKET_NAME}/{blob_path}")
    return uploaded_uris


def ensure_dataset(bq_client: bigquery.Client, location: str) -> None:
    dataset_ref = bigquery.Dataset(f"{PROJECT_ID}.{DATASET_ID}")
    dataset_ref.location = location
    try:
        bq_client.get_dataset(dataset_ref)
    except Exception:
        bq_client.create_dataset(dataset_ref, exists_ok=True)


def create_external_table(bq_client: bigquery.Client) -> None:
    table_ref = bigquery.Table(f"{PROJECT_ID}.{DATASET_ID}.{EXTERNAL_TABLE_ID}")
    external_config = bigquery.ExternalConfig("PARQUET")
    external_config.source_uris = [
        f"gs://{BUCKET_NAME}/{GCS_PREFIX}/yellow_tripdata_2024-*.parquet"
    ]
    external_config.autodetect = True
    table_ref.external_data_configuration = external_config
    bq_client.create_table(table_ref, exists_ok=True)


def create_materialized_table(bq_client: bigquery.Client) -> None:
    query = f"""
    CREATE OR REPLACE TABLE `{PROJECT_ID}.{DATASET_ID}.{MATERIALIZED_TABLE_ID}` AS
    SELECT * FROM `{PROJECT_ID}.{DATASET_ID}.{EXTERNAL_TABLE_ID}`
    """
    bq_client.query(query).result()


def create_partitioned_table(bq_client: bigquery.Client) -> None:
    query = f"""
    CREATE OR REPLACE TABLE `{PROJECT_ID}.{DATASET_ID}.{PARTITIONED_TABLE_ID}`
    PARTITION BY DATE(tpep_dropoff_datetime)
    CLUSTER BY VendorID
    OPTIONS (partition_expiration_days = 3650) AS
    SELECT * FROM `{PROJECT_ID}.{DATASET_ID}.{MATERIALIZED_TABLE_ID}`
    """
    bq_client.query(query).result()


def run_query(bq_client: bigquery.Client, query: str) -> Any:
    job = bq_client.query(query)
    return next(iter(job.result()))


def dry_run_bytes(bq_client: bigquery.Client, query: str) -> int:
    job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
    job = bq_client.query(query, job_config=job_config)
    return job.total_bytes_processed


def main() -> None:
    storage_client = storage.Client(project=PROJECT_ID)
    bq_client = bigquery.Client(project=PROJECT_ID)

    bucket = storage_client.bucket(BUCKET_NAME)
    bucket_location = bucket.location or "US"

    upload_parquet_files(storage_client)
    ensure_dataset(bq_client, bucket_location)

    create_external_table(bq_client)
    create_materialized_table(bq_client)
    create_partitioned_table(bq_client)

    results: dict[str, Any] = {}

    q1 = f"SELECT COUNT(*) AS cnt FROM `{PROJECT_ID}.{DATASET_ID}.{MATERIALIZED_TABLE_ID}`"
    results["q1_count"] = run_query(bq_client, q1).cnt

    q2_ext = (
        f"SELECT COUNT(DISTINCT PULocationID) FROM "
        f"`{PROJECT_ID}.{DATASET_ID}.{EXTERNAL_TABLE_ID}`"
    )
    q2_mat = (
        f"SELECT COUNT(DISTINCT PULocationID) FROM "
        f"`{PROJECT_ID}.{DATASET_ID}.{MATERIALIZED_TABLE_ID}`"
    )
    results["q2_ext_bytes"] = dry_run_bytes(bq_client, q2_ext)
    results["q2_mat_bytes"] = dry_run_bytes(bq_client, q2_mat)

    q3_one = f"SELECT PULocationID FROM `{PROJECT_ID}.{DATASET_ID}.{MATERIALIZED_TABLE_ID}`"
    q3_two = (
        f"SELECT PULocationID, DOLocationID FROM "
        f"`{PROJECT_ID}.{DATASET_ID}.{MATERIALIZED_TABLE_ID}`"
    )
    results["q3_one_bytes"] = dry_run_bytes(bq_client, q3_one)
    results["q3_two_bytes"] = dry_run_bytes(bq_client, q3_two)

    q4 = (
        f"SELECT COUNT(*) AS cnt FROM `{PROJECT_ID}.{DATASET_ID}.{MATERIALIZED_TABLE_ID}` "
        "WHERE fare_amount = 0"
    )
    results["q4_fare_zero"] = run_query(bq_client, q4).cnt

    q6_mat = (
        f"SELECT DISTINCT VendorID FROM `{PROJECT_ID}.{DATASET_ID}.{MATERIALIZED_TABLE_ID}` "
        "WHERE DATE(tpep_dropoff_datetime) BETWEEN '2024-03-01' AND '2024-03-15'"
    )
    q6_part = (
        f"SELECT DISTINCT VendorID FROM `{PROJECT_ID}.{DATASET_ID}.{PARTITIONED_TABLE_ID}` "
        "WHERE DATE(tpep_dropoff_datetime) BETWEEN '2024-03-01' AND '2024-03-15'"
    )
    results["q6_mat_bytes"] = dry_run_bytes(bq_client, q6_mat)
    results["q6_part_bytes"] = dry_run_bytes(bq_client, q6_part)

    q9 = f"SELECT COUNT(*) FROM `{PROJECT_ID}.{DATASET_ID}.{MATERIALIZED_TABLE_ID}`"
    results["q9_count_bytes"] = dry_run_bytes(bq_client, q9)

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
