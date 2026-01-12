import pandas as pd 
from sqlalchemy import create_engine
import pyarrow as pa
import fastparquet as fp

engine = create_engine("postgresql://root:root@localhost:5432/db_homework")

df = pd.read_parquet('green_tripdata_2025-11.parquet')


df.head(n=0).to_sql(name='green_taxi_data', con='engine', if_exists='replace', n_rows=0)