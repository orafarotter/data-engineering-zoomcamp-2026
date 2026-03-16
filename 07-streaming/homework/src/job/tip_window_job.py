from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import EnvironmentSettings, StreamTableEnvironment

def create_events_source_kafka(t_env):
    table_name = "events"
    source_ddl = f"""
    CREATE TABLE {table_name} (
        lpep_pickup_datetime VARCHAR,
        tip_amount DOUBLE,
        event_timestamp AS TO_TIMESTAMP(lpep_pickup_datetime, 'yyyy-MM-dd HH:mm:ss'),
        WATERMARK FOR event_timestamp AS event_timestamp - INTERVAL '5' SECOND
    ) WITH (
        'connector' = 'kafka',
        'properties.bootstrap.servers' = 'redpanda:29092',
        'topic' = 'green-trips',
        'scan.startup.mode' = 'earliest-offset',
        'format' = 'json'
    );
    """
    t_env.execute_sql(source_ddl)
    return table_name

def create_processed_events_sink_postgres(t_env):
    table_name = 'tip_window'
    sink_ddl = f"""
    CREATE TABLE {table_name} (        
        window_start TIMESTAMP,        
        total_tip_amount DOUBLE
    ) WITH (
        'connector' = 'jdbc',
        'url' = 'jdbc:postgresql://postgres:5432/postgres',
        'table-name' = '{table_name}',
        'username' = 'postgres',
        'password' = 'postgres',
        'driver' = 'org.postgresql.Driver'
    );
    """
    t_env.execute_sql(sink_ddl)
    return table_name

def log_processing():
    env = StreamExecutionEnvironment.get_execution_environment()
    env.enable_checkpointing(10 * 1000)  
    env.set_parallelism(1)

    settings = EnvironmentSettings.new_instance().in_streaming_mode().build()
    t_env = StreamTableEnvironment.create(env, environment_settings=settings)

    source_table = create_events_source_kafka(t_env)
    postgres_sink = create_processed_events_sink_postgres(t_env)

    t_env.execute_sql(
        f"""
        INSERT INTO {postgres_sink}
        SELECT
            TUMBLE_START(event_timestamp, INTERVAL '60' MINUTE) AS window_start,            
            SUM(tip_amount) AS total_tip_amount
        FROM {source_table}
        GROUP BY
            TUMBLE(event_timestamp, INTERVAL '60' MINUTE)
        """
    ).wait()

if __name__ == '__main__':
    log_processing()