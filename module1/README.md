# Question 1: Checking Docker Images
docker run -it --entrypoint bash python:3.13
pip --version

# Start Up Application Stack as Defined in Your docker-compose.yaml File
docker-compose up -d

# Download the Files to My Local Folder
wget https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2025-11.parquet
wget https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv

# Load Data to PostgreSQL DB
python3 ingest.py
docker exec -it postgres psql -U postgres -d ny_taxi

# Question 3: Counting short trips
psql (17.7)
Type "help" for help.

ny_taxi=# SELECT COUNT(*) 
ny_taxi-# FROM green_taxi_trips 
ny_taxi-# WHERE lpep_pickup_datetime >= '2025-11-01' 
ny_taxi-#   AND lpep_pickup_datetime < '2025-12-01' 
ny_taxi-#   AND trip_distance <= 1;
 count 
-------
  8007
(1 row)

# Question 4: Longest trip for each day
ny_taxi=# SELECT 
ny_taxi-#     DATE(lpep_pickup_datetime) AS pickup_day,
ny_taxi-#     MAX(trip_distance) AS max_distance
ny_taxi-# FROM green_taxi_trips
ny_taxi-# WHERE lpep_pickup_datetime >= '2025-11-01' 
ny_taxi-#   AND lpep_pickup_datetime < '2025-12-01'
ny_taxi-#   AND trip_distance < 100  -- Exclude erroneous outliers
ny_taxi-# GROUP BY pickup_day
ny_taxi-# ORDER BY max_distance DESC
ny_taxi-# LIMIT 1;
 pickup_day | max_distance 
------------+--------------
 2025-11-14 |        88.03
(1 row)

# Question 5: Biggest pickup zone
ny_taxi=# SELECT 
ny_taxi-#     z."Zone",
ny_taxi-#     SUM(t.total_amount) AS total_revenue
ny_taxi-# FROM green_taxi_trips t
ny_taxi-# JOIN zones z ON t."PULocationID" = z."LocationID"
ny_taxi-# WHERE t.lpep_pickup_datetime >= '2025-11-18' 
ny_taxi-#   AND t.lpep_pickup_datetime < '2025-11-19'
ny_taxi-# GROUP BY z."Zone"
ny_taxi-# ORDER BY total_revenue DESC
ny_taxi-# LIMIT 1;
       Zone        |   total_revenue   
-------------------+-------------------
 East Harlem North | 9281.919999999996
(1 row)

# Question 6: Largest tip
ny_taxi=# SELECT 
ny_taxi-#     z_drop."Zone",
ny_taxi-#     MAX(t.tip_amount) AS max_tip
ny_taxi-# FROM green_taxi_trips t
ny_taxi-# JOIN zones z_pick ON t."PULocationID" = z_pick."LocationID"
ny_taxi-# JOIN zones z_drop ON t."DOLocationID" = z_drop."LocationID"
ny_taxi-# WHERE z_pick."Zone" = 'East Harlem North'
ny_taxi-#   AND t.lpep_pickup_datetime >= '2025-11-01' 
ny_taxi-#   AND t.lpep_pickup_datetime < '2025-12-01'
ny_taxi-# GROUP BY z_drop."Zone"
ny_taxi-# ORDER BY max_tip DESC
ny_taxi-# LIMIT 1;
      Zone      | max_tip 
----------------+---------
 Yorkville West |   81.89
(1 row)

ny_taxi=# 