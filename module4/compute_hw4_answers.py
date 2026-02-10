#!/usr/bin/env python3
"""Compute DE Zoomcamp 2026 Module 4 homework answers (Q3-Q6)."""

import duckdb


def sql_list(urls):
    return "[" + ",".join(f"'{u}'" for u in urls) + "]"


def main() -> None:
    con = duckdb.connect()
    con.execute("INSTALL httpfs; LOAD httpfs;")

    months = [f"{m:02d}" for m in range(1, 13)]
    green_urls = [
        f"https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_{year}-{month}.csv.gz"
        for year in (2019, 2020)
        for month in months
    ]
    yellow_urls = [
        f"https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_{year}-{month}.csv.gz"
        for year in (2019, 2020)
        for month in months
    ]
    fhv_urls = [
        f"https://github.com/DataTalksClub/nyc-tlc-data/releases/download/fhv/fhv_tripdata_2019-{month}.csv.gz"
        for month in months
    ]

    query_q3_q5 = f"""
    with stg_green as (
        select
            cast(vendorid as integer) as vendor_id,
            try_cast(ratecodeid as integer) as rate_code_id,
            cast(pulocationid as integer) as pickup_location_id,
            cast(dolocationid as integer) as dropoff_location_id,
            cast(lpep_pickup_datetime as timestamp) as pickup_datetime,
            cast(lpep_dropoff_datetime as timestamp) as dropoff_datetime,
            cast(store_and_fwd_flag as varchar) as store_and_fwd_flag,
            cast(passenger_count as integer) as passenger_count,
            cast(trip_distance as double) as trip_distance,
            try_cast(trip_type as integer) as trip_type,
            cast(fare_amount as double) as fare_amount,
            cast(extra as double) as extra,
            cast(mta_tax as double) as mta_tax,
            cast(tip_amount as double) as tip_amount,
            cast(tolls_amount as double) as tolls_amount,
            cast(ehail_fee as double) as ehail_fee,
            cast(improvement_surcharge as double) as improvement_surcharge,
            cast(total_amount as double) as total_amount,
            try_cast(payment_type as integer) as payment_type
        from read_csv_auto({sql_list(green_urls)}, union_by_name=true)
        where vendorid is not null
    ),

    stg_yellow as (
        select
            cast(vendorid as integer) as vendor_id,
            cast(ratecodeid as integer) as rate_code_id,
            cast(pulocationid as integer) as pickup_location_id,
            cast(dolocationid as integer) as dropoff_location_id,
            cast(tpep_pickup_datetime as timestamp) as pickup_datetime,
            cast(tpep_dropoff_datetime as timestamp) as dropoff_datetime,
            cast(store_and_fwd_flag as varchar) as store_and_fwd_flag,
            cast(passenger_count as integer) as passenger_count,
            cast(trip_distance as double) as trip_distance,
            cast(1 as integer) as trip_type,
            cast(fare_amount as double) as fare_amount,
            cast(extra as double) as extra,
            cast(mta_tax as double) as mta_tax,
            cast(tip_amount as double) as tip_amount,
            cast(tolls_amount as double) as tolls_amount,
            cast(0 as double) as ehail_fee,
            cast(improvement_surcharge as double) as improvement_surcharge,
            cast(total_amount as double) as total_amount,
            cast(payment_type as integer) as payment_type
        from read_csv_auto({sql_list(yellow_urls)}, union_by_name=true)
        where vendorid is not null
    ),

    int_trips_unioned as (
        select *, 'Green' as service_type from stg_green
        union all
        select *, 'Yellow' as service_type from stg_yellow
    ),

    int_trips as (
        select *
        from int_trips_unioned
        qualify row_number() over(
            partition by vendor_id, pickup_datetime, pickup_location_id, service_type
            order by dropoff_datetime
        ) = 1
    ),

    dim_zones as (
        select
            cast(locationid as integer) as location_id,
            borough,
            zone,
            service_zone
        from read_csv_auto('https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv')
    ),

    fct_trips as (
        select
            trips.*,
            pz.zone as pickup_zone,
            dz.zone as dropoff_zone
        from int_trips as trips
        left join dim_zones as pz
          on trips.pickup_location_id = pz.location_id
        left join dim_zones as dz
          on trips.dropoff_location_id = dz.location_id
    ),

    fct_monthly_zone_revenue as (
        select
            coalesce(pickup_zone, 'Unknown Zone') as pickup_zone,
            date_trunc('month', pickup_datetime) as revenue_month,
            service_type,
            sum(fare_amount) as revenue_monthly_fare,
            sum(extra) as revenue_monthly_extra,
            sum(mta_tax) as revenue_monthly_mta_tax,
            sum(tip_amount) as revenue_monthly_tip_amount,
            sum(tolls_amount) as revenue_monthly_tolls_amount,
            sum(ehail_fee) as revenue_monthly_ehail_fee,
            sum(improvement_surcharge) as revenue_monthly_improvement_surcharge,
            sum(total_amount) as revenue_monthly_total_amount,
            count(*) as total_monthly_trips
        from fct_trips
        group by 1, 2, 3
    )
    select
      (select count(*) from fct_monthly_zone_revenue) as q3_count,
      (select pickup_zone
       from fct_monthly_zone_revenue
       where service_type='Green' and revenue_month >= '2020-01-01' and revenue_month < '2021-01-01'
       order by revenue_monthly_total_amount desc
       limit 1
      ) as q4_zone,
      (select sum(total_monthly_trips)
       from fct_monthly_zone_revenue
       where service_type='Green' and revenue_month='2019-10-01'
      ) as q5_total_trips
    ;
    """

    q3_count, q4_zone, q5_total_trips = con.execute(query_q3_q5).fetchone()

    query_q6 = f"""
    select count(*)
    from read_csv_auto({sql_list(fhv_urls)}, union_by_name=true)
    where dispatching_base_num is not null
    """
    q6_count = con.execute(query_q6).fetchone()[0]

    print("Q3 count(fct_monthly_zone_revenue):", int(q3_count))
    print("Q4 highest green zone (2020):", q4_zone)
    print("Q5 green trips in 2019-10:", int(q5_total_trips))
    print("Q6 count(stg_fhv_tripdata):", int(q6_count))


if __name__ == "__main__":
    main()
