import os
import io
import requests
import pandas as pd
import pyarrow.parquet as pq
from sqlalchemy import create_engine
from tqdm.auto import tqdm
import click

def ingest_data(engine, url_zones, url_trips, table_name_zones, table_name_trips): 
    # Inserting ZONE data into the database.
    try:
        df_zones = pd.read_csv(url_zones)        
        
        df_zones.to_sql(name=table_name_zones, con=engine, if_exists='replace')
        print(f"Table '{table_name_zones}' created!")        
    except Exception as e:
        print(f"Error processing '{table_name_zones}': {e}")

    print("\n")

    # Inserting TRIP data into the database.
    try:
        # Downloading the parquet file to memory.
        response = requests.get(url_trips)
        file_buffer = io.BytesIO(response.content)
        parquet_file = pq.ParquetFile(file_buffer)
        
        # Iterating over the chunks (row groups) of the parquet
        for i in tqdm(range(parquet_file.num_row_groups), desc="Loading tripdata"):
            
            # Loading only one chunk into memory.
            df_chunk = parquet_file.read_row_group(i).to_pandas()

            # Converting columns from int32 to int64.
            cols_to_convert = ['VendorID', 'PULocationID', 'DOLocationID']
            df_chunk[cols_to_convert] = df_chunk[cols_to_convert].astype('int64')

            # If it's the first chunk, replace the table to start fresh.
            # For subsequent chunks, append to the existing table.
            mode = 'replace' if i == 0 else 'append'            
            df_chunk.to_sql(name=table_name_trips, con=engine, if_exists=mode, index=False) 
            #index=False to prevent Pandas from creating an unnecessary extra column in your database.           

        print(f"Table '{table_name_trips}' created!")

    except Exception as e:
        print(f"Error processing '{table_name_trips}': {e}")

@click.command()
#@click.option('--pg-user', default='root',help='Postgres user') #show_default=True
#@click.option('--pg-host', default='localhost',  help='Postgres host')
#@click.option('--pg-port', default=5432,  type=int, help='Postgres port')
#@click.option('--pg-db', default='green_tripdata',  help='Postgres database')
@click.option('--pg-user', default=lambda: os.environ.get('DB_USER', 'root'),help='Postgres user') #show_default=True
@click.option('--pg-pass', default=lambda: os.environ.get('DB_PASSWORD', ''),  help='Postgres password')
@click.option('--pg-host', default=lambda: os.environ.get('DB_HOST', 'localhost'),  help='Postgres host')
@click.option('--pg-port', default=lambda: int(os.environ.get('DB_PORT', '5432')),  type=int, help='Postgres port')
@click.option('--pg-db', default=lambda: os.environ.get('DB_NAME', 'green_tripdata'),  help='Postgres database')
@click.option('--year', default=2025,  type=int, help='Year for the trip data')
@click.option('--month', default=11,  type=int, help='Month for the trip data')
@click.option('--table-name-zones', default='taxi_zone_lookup',  help='Table name for zones')
@click.option('--table-name-trips', default=None, help='Table name for trips (computed from year/month if omitted)')
def main(pg_user, pg_pass, pg_host, pg_port, pg_db, year, month, table_name_zones, table_name_trips):
    # Compute trips table name if not provided
    if table_name_trips is None:
        table_name_trips = f'tripdata_{year}_{month:02d}'

    url_zones = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv'
    url_trips = f'https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_{year}-{month:02d}.parquet'

    engine = create_engine(f'postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}')

    print("Connection with the database established.")
   
    ingest_data(
        engine=engine,
        url_zones=url_zones,
        url_trips=url_trips,
        table_name_zones=table_name_zones,
        table_name_trips=table_name_trips
    )

if __name__ == '__main__':
    main()