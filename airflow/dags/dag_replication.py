from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from datetime import datetime

default_args = {
    'start_date': datetime(2023, 1, 1),
    'catchup': False
}

with DAG(
    dag_id='dag_replication',
    default_args=default_args,
    schedule_interval='@daily',
    description='Replicate data from PostgreSQL to MySQL using Spark'
) as dag:

    replicate_task = SparkSubmitOperator(
        task_id='replicate_postgres_to_mysql',
        application='/opt/spark_scripts/transform_and_load_spark.py',
        conn_id='spark_default',
        verbose=True,
        conf={'spark.master': 'spark://spark:7077'}
    )

    replicate_task