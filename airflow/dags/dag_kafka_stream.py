from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from datetime import datetime

default_args = {
    'start_date': datetime(2023, 1, 1),
    'catchup': False
}

with DAG(
    dag_id='dag_kafka_stream',
    default_args=default_args,
    schedule_interval='@hourly',
    description='Read data from Kafka and load into PostgreSQL via Spark'
) as dag:

    kafka_to_pg = SparkSubmitOperator(
        task_id='kafka_to_postgres',
        application='/opt/spark_scripts/kafka_to_postgres.py',
        conn_id='spark_default',
        verbose=True,
        conf={'spark.master': 'spark://spark:7077'}
    )

    kafka_to_pg