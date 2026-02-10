## Module 1 - Docker + PostgreSQL + SQL

This folder contains my Homework 1 work for Data Engineering Zoomcamp 2026.

## Objective

Build a local data environment with Docker, ingest NYC Taxi data into PostgreSQL, and answer SQL questions from that loaded dataset.

## Concepts Used

- Containerization with Docker and Docker Compose
- Persistent volumes for database and pgAdmin state
- Programmatic ingestion from file formats (`parquet`, `csv`) into PostgreSQL
- Relational querying with SQL (`COUNT`, `GROUP BY`, `JOIN`, `ORDER BY`, filters)

## Course Concept Mapping (What and Where)

- Docker containers and services (Module 1 Docker section): implemented in `module1/docker-compose.yaml` with `postgres` and `pgadmin` services.
- Port mapping and host-container networking: `5433:5432` in `module1/docker-compose.yaml`, used by SQLAlchemy URL in `module1/ingest.py`.
- Persistence with Docker volumes: `vol-pgdata` and `vol-pgadmin_data` in `module1/docker-compose.yaml`.
- Data ingestion with Python (Pandas + SQLAlchemy): `module1/ingest.py` (`read_parquet`, `read_csv`, `to_sql`).
- SQL refresher concepts:
  - filtering and counting: Question 3 query (`WHERE` + `COUNT(*)`)
  - aggregations and grouping: Question 4/5 (`MAX`, `SUM`, `GROUP BY`)
  - joins for enrichment: Question 5/6 join `green_taxi_trips` with `zones`.

## Files and What They Do

- `docker-compose.yaml`
  - Starts two services: `postgres` and `pgadmin`
  - Maps PostgreSQL to host port `5433` and pgAdmin to `8080`
  - Uses named volumes (`vol-pgdata`, `vol-pgadmin_data`) so data survives container restarts

- `ingest.py`
  - Connects to PostgreSQL using SQLAlchemy
  - Reads `green_tripdata_2025-11.parquet` into a Pandas DataFrame
  - Writes DataFrame to table `green_taxi_trips`
  - Reads `taxi_zone_lookup.csv`
  - Writes lookup data to table `zones`

- `green_tripdata_2025-11.parquet`, `taxi_zone_lookup.csv`
  - Input datasets used for loading and analysis

## Step-by-Step Workflow

1. Start infra:

```bash
docker-compose up -d
```

2. (Question 1) Check Python image / pip version:

```bash
docker run -it --entrypoint bash python:3.13
pip --version
```

3. Load data into PostgreSQL:

```bash
python3 ingest.py
```

4. Connect to DB for SQL answers:

```bash
docker exec -it postgres psql -U postgres -d ny_taxi
```

## How the SQL Produced the Answers

### Question 3 - Counting short trips

```sql
SELECT COUNT(*)
FROM green_taxi_trips
WHERE lpep_pickup_datetime >= '2025-11-01'
  AND lpep_pickup_datetime < '2025-12-01'
  AND trip_distance <= 1;
```

- Logic: month filter + trip distance threshold (`<= 1 mile`)
- Result: **8007**

### Question 4 - Longest trip day in November

```sql
SELECT
    DATE(lpep_pickup_datetime) AS pickup_day,
    MAX(trip_distance) AS max_distance
FROM green_taxi_trips
WHERE lpep_pickup_datetime >= '2025-11-01'
  AND lpep_pickup_datetime < '2025-12-01'
  AND trip_distance < 100
GROUP BY pickup_day
ORDER BY max_distance DESC
LIMIT 1;
```

- Logic: compute daily maximum distance, remove extreme outliers (`trip_distance < 100`), pick highest day
- Result: **2025-11-14** with **88.03** miles

### Question 5 - Biggest pickup zone by revenue on 2025-11-18

```sql
SELECT
    z."Zone",
    SUM(t.total_amount) AS total_revenue
FROM green_taxi_trips t
JOIN zones z ON t."PULocationID" = z."LocationID"
WHERE t.lpep_pickup_datetime >= '2025-11-18'
  AND t.lpep_pickup_datetime < '2025-11-19'
GROUP BY z."Zone"
ORDER BY total_revenue DESC
LIMIT 1;
```

- Logic: join trip records with zone names, aggregate `total_amount` by pickup zone, select top zone
- Result: **East Harlem North** (`9281.92`)

### Question 6 - Largest tip from East Harlem North pickups

```sql
SELECT
    z_drop."Zone",
    MAX(t.tip_amount) AS max_tip
FROM green_taxi_trips t
JOIN zones z_pick ON t."PULocationID" = z_pick."LocationID"
JOIN zones z_drop ON t."DOLocationID" = z_drop."LocationID"
WHERE z_pick."Zone" = 'East Harlem North'
  AND t.lpep_pickup_datetime >= '2025-11-01'
  AND t.lpep_pickup_datetime < '2025-12-01'
GROUP BY z_drop."Zone"
ORDER BY max_tip DESC
LIMIT 1;
```

- Logic: filter trips by pickup zone, find max `tip_amount` by dropoff zone, return highest
- Result: **Yorkville West** (`81.89`)

## Summary of Captured Results

- Q3: **8007**
- Q4: **2025-11-14 (88.03)**
- Q5: **East Harlem North (9281.92)**
- Q6: **Yorkville West (81.89)**
