import gzip
import urllib.request

BASE_URL = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/{taxi}/{file}.csv.gz"


def count_rows_and_size(url: str) -> tuple[int, int]:
    with urllib.request.urlopen(url) as resp:
        gz = gzip.GzipFile(fileobj=resp)
        total_size = 0
        line_count = 0
        while True:
            chunk = gz.read(1024 * 1024)
            if not chunk:
                break
            total_size += len(chunk)
            line_count += chunk.count(b"\n")
    if line_count > 0:
        line_count -= 1
    return line_count, total_size


def main() -> None:
    months = [f"{m:02d}" for m in range(1, 13)]

    q1_file = "yellow_tripdata_2020-12"
    q1_url = BASE_URL.format(taxi="yellow", file=q1_file)
    q1_rows, q1_size_bytes = count_rows_and_size(q1_url)
    q1_size_mib = q1_size_bytes / (1024**2)
    print("Q1 rows:", q1_rows)
    print("Q1 size MiB:", round(q1_size_mib, 1))

    yellow_2020_total = 0
    for month in months:
        file = f"yellow_tripdata_2020-{month}"
        url = BASE_URL.format(taxi="yellow", file=file)
        rows, _ = count_rows_and_size(url)
        yellow_2020_total += rows
    print("Q3 yellow_2020_total:", yellow_2020_total)

    green_2020_total = 0
    for month in months:
        file = f"green_tripdata_2020-{month}"
        url = BASE_URL.format(taxi="green", file=file)
        rows, _ = count_rows_and_size(url)
        green_2020_total += rows
    print("Q4 green_2020_total:", green_2020_total)

    q5_file = "yellow_tripdata_2021-03"
    q5_url = BASE_URL.format(taxi="yellow", file=q5_file)
    q5_rows, _ = count_rows_and_size(q5_url)
    print("Q5 rows:", q5_rows)


if __name__ == "__main__":
    main()
