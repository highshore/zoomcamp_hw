import pandas as pd
from sqlalchemy import create_engine

# 1. Connect to the database
# Note: We use port 5433 because we are connecting from the HOST machine
engine = create_engine('postgresql://postgres:postgres@localhost:5433/ny_taxi')

# 2. Load Green Taxi Data
print("Loading Green Taxi Data...")
df = pd.read_parquet('green_tripdata_2025-11.parquet')
df.to_sql(name='green_taxi_trips', con=engine, if_exists='replace', index=False)
print("Green Taxi Data Loaded.")

# 3. Load Zones Data
print("Loading Zones Data...")
df_zones = pd.read_csv('taxi_zone_lookup.csv')
df_zones.to_sql(name='zones', con=engine, if_exists='replace', index=False)
print("Zones Data Loaded.")