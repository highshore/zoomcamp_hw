## Module 4 - Analytics Engineering (dbt)

This folder contains my Homework 4 work for Data Engineering Zoomcamp 2026.

## Objective

Apply dbt-style analytics engineering transformations to NYC Taxi datasets and compute the homework outputs reproducibly.

## Concepts Used

- Layered modeling: staging -> intermediate -> marts
- Schema standardization and type casting
- Unioning heterogeneous sources (Green + Yellow)
- Deduplication with window functions
- Dimensional enrichment via zone lookup joins
- Aggregation to reporting mart (`fct_monthly_zone_revenue`)
- FHV staging rule: `dispatching_base_num is not null`

## Files and What They Do

- `compute_hw4_answers.py`
  - Recreates the dbt model logic in DuckDB SQL
  - Reads source files directly from official release URLs
  - Computes Q3-Q6 outputs exactly and prints them

- `stg_fhv_tripdata.sql`
  - dbt staging model for FHV required by Question 6
  - Renames columns to project naming
  - Casts types
  - Filters null `dispatching_base_num`

## How the Script Produces Answers (Step-by-Step)

### 1) Build source URL lists

- Green: 2019-2020 monthly CSVs
- Yellow: 2019-2020 monthly CSVs
- FHV: 2019 monthly CSVs

### 2) Build dbt-equivalent transformations in SQL CTEs

The SQL in `compute_hw4_answers.py` follows this flow:

1. `stg_green`
   - type-casts and renames green columns
   - filters `vendorid is not null`

2. `stg_yellow`
   - type-casts and renames yellow columns
   - sets yellow-only defaults (`trip_type=1`, `ehail_fee=0`)
   - filters `vendorid is not null`

3. `int_trips_unioned`
   - `UNION ALL` green and yellow with `service_type`

4. `int_trips`
   - deduplicates using:
     - partition key: `vendor_id, pickup_datetime, pickup_location_id, service_type`
     - keep earliest `dropoff_datetime`

5. `dim_zones`
   - loads taxi zone lookup dimension

6. `fct_trips`
   - joins trips with pickup/dropoff zone names

7. `fct_monthly_zone_revenue`
   - monthly + zone + service_type aggregation
   - computes monthly revenue components and trip counts

### 3) Compute Q3, Q4, Q5

- Q3: `count(*)` from `fct_monthly_zone_revenue`
- Q4: max `revenue_monthly_total_amount` for `service_type='Green'` in 2020
- Q5: sum `total_monthly_trips` for Green in `2019-10`

### 4) Compute Q6

Separate FHV query:

- reads all FHV 2019 monthly files
- counts rows where `dispatching_base_num is not null`

## Step-by-Step to Reproduce

Create environment:

```bash
python3 -m venv .venv_hw4
. .venv_hw4/bin/activate
python -m pip install --upgrade pip
python -m pip install duckdb
```

Run:

```bash
python compute_hw4_answers.py
```

## Answers

1. `dbt run --select int_trips_unioned`: **builds `int_trips_unioned` only**
2. New `payment_type=6` with accepted values `[1,2,3,4,5]`: **dbt test fails (non-zero exit)**
3. Count of rows in `fct_monthly_zone_revenue`: **12,184**
4. Highest Green revenue zone in 2020: **East Harlem North**
5. Green total trips in October 2019: **384,624**
6. Count in `stg_fhv_tripdata`: **43,244,693**

## Why This Approach

- Keeps logic transparent and close to dbt models.
- Produces reproducible outputs from raw public data.
- Makes each answer traceable to a specific transformation step.
