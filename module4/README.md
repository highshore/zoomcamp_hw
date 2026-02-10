## Module 4 - Analytics Engineering (dbt)

This folder contains my Homework 4 work for the Data Engineering Zoomcamp 2026.

### Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv_hw4
. .venv_hw4/bin/activate
python -m pip install --upgrade pip
python -m pip install duckdb
```

Run the script:

```bash
python compute_hw4_answers.py
```

### Answers

1) If you run `dbt run --select int_trips_unioned`, it builds: **`int_trips_unioned` only**  
2) If `payment_type = 6` appears and accepted values are `[1,2,3,4,5]`, `dbt test` will: **fail with non-zero exit code**  
3) Count of records in `fct_monthly_zone_revenue`: **12,184**  
4) Highest Green taxi revenue zone in 2020: **East Harlem North**  
5) Green taxi total trips in October 2019: **384,624**  
6) Count of records in `stg_fhv_tripdata` (`dispatching_base_num is not null`): **43,244,693**

### Notes

- `compute_hw4_answers.py` computes Questions 3-6 directly from official NYC TLC release files with DuckDB.
- `stg_fhv_tripdata.sql` shows the staging model used for Question 6.
