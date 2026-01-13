import io
import requests
import pandas as pd
import pyarrow.parquet as pq
from sqlalchemy import create_engine
from tqdm.auto import tqdm

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
            # Verifica se as colunas existem antes de tentar converter
            cols_existentes = [c for c in cols_para_converter if c in df_chunk.columns]
            df_chunk[cols_existentes] = df_chunk[cols_existentes].astype('int64')

            # Na 1ª iteração faz 'replace' para criar a tabela, nas seguintes faz 'append'
            mode = 'replace' if i == 0 else 'append'            
            df_chunk.to_sql(name=table_name_trips, con=engine, if_exists=mode, index=False)            

        print(f"Tabela '{table_name_trips}' criada!")

    except Exception as e:
        print(f"Erro ao processar '{table_name_trips}': {e}")


def main():
    # Parâmetros de Conexão 
    pg_user = 'root'
    pg_pass = 'root'
    pg_host = 'localhost'
    pg_port = '5432'
    pg_db   = 'green_tripdata'
    
    year = 2025
    month = 11
    table_name_zones = 'taxi_zone_lookup'
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