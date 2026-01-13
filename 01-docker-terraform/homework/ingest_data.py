import io
import requests
import pandas as pd
import pyarrow.parquet as pq
from sqlalchemy import create_engine
from tqdm.auto import tqdm
import click

def ingest_data(engine, url_zones, url_trips, table_name_zones, table_name_trips): 
    # Inserindo dados de ZONAS no banco
    try:
        df_zones = pd.read_csv(url_zones)        
        
        df_zones.to_sql(name=table_name_zones, con=engine, if_exists='replace')
        print(f"Tabela '{table_name_zones}' criada!")        
    except Exception as e:
        print(f"Erro ao processar '{table_name_zones}': {e}")

    print("\n")

    # Inserindo dados de VIAGENS no banco
    try:
        # Baixando o arquivo parquet para a memória
        response = requests.get(url_trips)
        file_buffer = io.BytesIO(response.content)
        parquet_file = pq.ParquetFile(file_buffer)
        
        # Iterando sobre os chunks (row groups) do parquet
        for i in tqdm(range(parquet_file.num_row_groups), desc="Carregando tripdata"):
            
            # Carrega apenas um chunk para a memória
            df_chunk = parquet_file.read_row_group(i).to_pandas()

            # Conversão das colunas int32 para int64 
            cols_para_converter = ['VendorID', 'PULocationID', 'DOLocationID']
            df_chunk[cols_para_converter] = df_chunk[cols_para_converter].astype('int64')

            # Na 1ª iteração faz 'replace' para criar a tabela, nas seguintes faz 'append'
            mode = 'replace' if i == 0 else 'append'            
            df_chunk.to_sql(name=table_name_trips, con=engine, if_exists=mode, index=False)            

        print(f"Tabela '{table_name_trips}' criada!")

    except Exception as e:
        print(f"Erro ao processar '{table_name_trips}': {e}")


@click.command()
@click.option('--pg-user', default='root',help='Postgres user') #show_default=True
@click.option('--pg-pass', default='root',  help='Postgres password')
@click.option('--pg-host', default='localhost',  help='Postgres host')
@click.option('--pg-port', default=5432,  type=int, help='Postgres port')
@click.option('--pg-db', default='green_tripdata',  help='Postgres database')
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

    print("Conexão com o banco estabelecida.")

    # Chamada da função de ingestão
    ingest_data(
        engine=engine,
        url_zones=url_zones,
        url_trips=url_trips,
        table_name_zones=table_name_zones,
        table_name_trips=table_name_trips
    )

if __name__ == '__main__':
    main()