"""@bruin

name: ingestion.trips
connection: duckdb-default

materialization:
  type: table
  strategy: append
image: python:3.11

columns:
  - name: pickup_datetime
    type: timestamp
  - name: dropoff_datetime
    type: timestamp
  - name: pickup_location_id
    type: integer
  - name: dropoff_location_id
    type: integer
  - name: fare_amount
    type: float
  - name: taxi_type
    type: varchar
  - name: payment_type
    type: integer

@bruin"""

import os
import json
import pandas as pd


def materialize():
    start_date = os.environ["BRUIN_START_DATE"]
    end_date = os.environ["BRUIN_END_DATE"]
    taxi_types = json.loads(os.environ["BRUIN_VARS"]).get(
        "taxi_types", ["yellow"])

    start_dt = pd.to_datetime(start_date).replace(day=1)
    end_dt = pd.to_datetime(end_date)
    months = pd.date_range(start=start_dt, end=end_dt, freq="MS")

    col_map = {
        "tpep_pickup_datetime": "pickup_datetime",
        "tpep_dropoff_datetime": "dropoff_datetime",
        "lpep_pickup_datetime": "pickup_datetime",
        "lpep_dropoff_datetime": "dropoff_datetime",
        "pulocationid": "pickup_location_id",
        "dolocationid": "dropoff_location_id",
    }

    expected_cols = [
        "pickup_datetime",
        "dropoff_datetime",
        "pickup_location_id",
        "dropoff_location_id",
        "fare_amount",
        "taxi_type",
        "payment_type",
    ]

    dataframes = []

    for taxi in taxi_types:
        for dt in months:
            url = f"https://d37ci6vzurychx.cloudfront.net/trip-data/{taxi}_tripdata_{dt.strftime('%Y-%m')}.parquet"

            try:
                df = pd.read_parquet(url)
                df.columns = df.columns.str.lower()

                cols_to_keep = list(col_map.keys()) + \
                    ["fare_amount", "payment_type"]
                available_cols = [c for c in cols_to_keep if c in df.columns]
                df = df[available_cols]

                df = df.rename(columns=col_map)
                df['taxi_type'] = taxi

                if 'pickup_location_id' in df.columns:
                    df['pickup_location_id'] = pd.to_numeric(
                        df['pickup_location_id'], downcast='integer')
                if 'dropoff_location_id' in df.columns:
                    df['dropoff_location_id'] = pd.to_numeric(
                        df['dropoff_location_id'], downcast='integer')
                if 'payment_type' in df.columns:
                    df['payment_type'] = pd.to_numeric(
                        df['payment_type'], downcast='integer')
                if 'fare_amount' in df.columns:
                    df['fare_amount'] = pd.to_numeric(
                        df['fare_amount'], downcast='float')

                df['taxi_type'] = df['taxi_type'].astype('category')

                for col in expected_cols:
                    if col not in df.columns:
                        df[col] = None
                df = df[expected_cols]

                dataframes.append(df)
                print(f"Loaded {len(df)} rows from {url}")

            except Exception as e:
                print(f"Skipped {taxi} for {dt.strftime('%Y-%m')}: {e}")

    if dataframes:
        final_dataframe = pd.concat(dataframes, ignore_index=True)
    else:
        final_dataframe = pd.DataFrame(columns=expected_cols)

    return final_dataframe
