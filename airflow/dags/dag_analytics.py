from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from datetime import datetime

default_args = {
    'start_date': datetime(2023, 1, 1),
    'catchup': False
}

with DAG(
    dag_id='dag_analytics',
    default_args=default_args,
    schedule_interval='@daily',
    description='Create analytics views in MySQL using Spark'
) as dag:

    create_analytics_views = SparkSubmitOperator(
        task_id='create_analytics_views',
        application='/opt/spark_scripts/create_analytics_views_spark.py',
        conn_id='spark_default',
        verbose=True,
        conf={'spark.master': 'spark://spark:7077'}
    )

    create_analytics_views