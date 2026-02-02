## Module 2 - Workflow Orchestration (Kestra)

This folder contains my Homework 2 work for the Data Engineering Zoomcamp 2026.

### Answers

1) 128.3 MiB  
2) `green_tripdata_2020-04.csv`  
3) 24,648,499  
4) 1,734,051  
5) 1,925,152  
6) Add a `timezone` property set to `America/New_York` in the Schedule trigger configuration

### How I computed the counts and size

The script `compute_hw2_answers.py` streams the gzipped CSVs from the official
GitHub releases, decompresses on the fly, counts rows (excluding the header),
and sums uncompressed bytes to compute the size in MiB.

Run it from this folder:

```bash
python3 compute_hw2_answers.py
```
