## Module 2 - Workflow Orchestration (Kestra)

This folder contains my Homework 2 work for Data Engineering Zoomcamp 2026.

## Objective

Compute Homework 2 numeric answers from NYC TLC release files using a reproducible script instead of manual counting.

## Concepts Used

- Streaming downloads over HTTP (`urllib.request`)
- On-the-fly gzip decompression (`gzip.GzipFile`)
- Memory-efficient chunk processing (1 MiB chunks)
- Programmatic row counting and file-size aggregation
- Deterministic monthly loops to avoid manual mistakes

## Course Concept Mapping (What and Where)

- Workflow orchestration mindset (Module 2): represented by codifying repeatable steps in `module2/compute_hw2_answers.py` instead of one-off manual counting.
- Parameterized, reusable data pipeline logic: URL template `BASE_URL` and monthly loop in `main()` of `module2/compute_hw2_answers.py`.
- Efficient data processing for large files:
  - streaming HTTP reads (`urllib.request.urlopen`)
  - chunk-based processing (`gz.read(1024 * 1024)`)
  - incremental metrics (`line_count`, `total_size`) in `count_rows_and_size`.
- Reliable metric extraction:
  - row counting by newline count
  - header adjustment (`line_count -= 1`) to produce data-row totals only.
- Reproducibility and automation: single command run (`python3 compute_hw2_answers.py`) generates consistent Q1/Q3/Q4/Q5 outputs.

## File and What It Does

- `compute_hw2_answers.py`
  - Builds file URLs from a template
  - Streams and decompresses each `.csv.gz`
  - Counts newline characters to estimate row count
  - Subtracts one header row when present
  - Aggregates monthly totals for 2020 yellow and green datasets
  - Prints answers for Q1, Q3, Q4, Q5

## Code Walkthrough

### `count_rows_and_size(url)`

1. Opens the remote file URL.
2. Wraps response in `gzip.GzipFile`.
3. Reads decompressed data in fixed chunks.
4. Tracks:
   - total decompressed bytes (`total_size`)
   - number of line breaks (`line_count`)
5. Subtracts header row (`line_count -= 1`) if file has lines.
6. Returns `(row_count, bytes)`.

### `main()`

1. Defines `months = ['01'..'12']`.
2. Q1: reads `yellow_tripdata_2020-12` and computes MiB.
3. Q3: loops all yellow 2020 months and sums row counts.
4. Q4: loops all green 2020 months and sums row counts.
5. Q5: reads `yellow_tripdata_2021-03` row count.

## Step-by-Step to Reproduce

```bash
python3 compute_hw2_answers.py
```

The script prints each answer directly.

## Answers

1. **128.3 MiB**
2. **`green_tripdata_2020-04.csv`**
3. **24,648,499**
4. **1,734,051**
5. **1,925,152**
6. Add `timezone: America/New_York` to the schedule trigger config

## Why This Approach

- Avoids downloading full files to disk.
- Keeps memory usage stable.
- Makes answers reproducible and auditable with code.
