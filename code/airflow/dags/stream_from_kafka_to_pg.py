import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.operators.empty import EmptyOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook

from scripts.helpers.airflow_common import get_connection_uri

# ================================
# Константы
# ================================

# Путь к JAR-файлу PostgreSQL коннектора, необходимому для подключения Spark к PostgreSQL
JARS = "/opt/airflow/spark/jars/postgresql-42.2.18.jar"

# Путь к PySpark-скрипту, который будет выполнять стриминговую обработку данных из Kafka в PostgreSQL
PYSPARK_SCRIPT_PATH = '/opt/airflow/scripts/pyspark_scripts/stream_from_kafka_to_pg.py'

# ================================
# Параметры по умолчанию для DAG
# ================================

default_args = {
    'owner': 'airflow',  # Владелец DAG'а
    'depends_on_past': False,  # Не зависит от предыдущих запусков DAG'а
    'start_date': datetime(year=2025, month=1, day=9),  # Дата начала выполнения DAG'а
    'email_on_failure': False,  # Не отправлять email при сбое задачи
    'email_on_retry': False,  # Не отправлять email при повторных попытках
    'retries': 0,  # Количество попыток повторного выполнения задачи при сбое
    'retry_delay': timedelta(minutes=5),  # Задержка между попытками повторного выполнения
    'catchup': True,  # Выполнять "догоняющие" запуски для пропущенных интервалов
    'concurrency': 1  # Максимальное количество задач, выполняющихся одновременно для одного DAG'а
}

# ================================
# Определение DAG
# ================================

with DAG(
        'kafka_to_postgres_streaming',  # Идентификатор DAG'а
        default_args=default_args,  # Использование ранее определённых параметров по умолчанию
        description='Стриминговое чтение пользователей из Kafka и запись в Postgres',  # Описание DAG'а
        schedule_interval=timedelta(days=1),  # Интервал планирования: ежедневно
        concurrency=1,  # Максимальное количество задач, выполняющихся одновременно в этом DAG'е
        max_active_runs=1  # Максимальное количество активных запусков DAG'а одновременно
) as dag:
    # ================================
    # Креды и драйверы
    # ================================

    # Получение URI подключения к Kafka с использованием переменных окружения или значений по умолчанию
    kafka_bootstrap_servers = os.getenv('KAFKA_INTERNAL_CONNECT_PATH', 'kafka:29092')

    # Получение имени темы Kafka из переменных окружения или значения по умолчанию
    kafka_topic = os.getenv('KAFKA_TOPIC_NAME', 'users-data')

    # Получение URI подключения к целевой базе данных PostgreSQL с использованием хука PostgresHook
    target_url = get_connection_uri(PostgresHook.get_connection('coursework_de_postgresql'))

    # Определение класса драйвера JDBC для подключения к PostgreSQL
    target_driver = 'org.postgresql.Driver'

    # Определение имени целевой таблицы в PostgreSQL, куда будут записываться данные
    target_table = 'users'

    # ================================
    # Определение задач DAG
    # ================================

    # Начальная задача DAG, не выполняет никаких действий
    start = EmptyOperator(task_id='start')

    # Конечная задача DAG, не выполняет никаких действий
    finish = EmptyOperator(task_id='finish')

    # Определение задачи SparkSubmitOperator для стриминговой обработки данных из Kafka в PostgreSQL
    spark_submit_task = SparkSubmitOperator(
        task_id='spark_kafka_to_postgres',  # Уникальный идентификатор задачи
        application=PYSPARK_SCRIPT_PATH,  # Путь к PySpark-скрипту для выполнения
        conn_id='coursework_de_spark',  # Идентификатор подключения Spark, настроенный в Airflow
        application_args=[
            '--kafka_bootstrap_servers', kafka_bootstrap_servers,  # Аргумент: URI подключения к Kafka
            '--kafka_topic', kafka_topic,  # Аргумент: Название темы Kafka для чтения данных
            '--target_url', target_url,  # Аргумент: URI подключения к PostgreSQL
            '--target_driver', target_driver,  # Аргумент: Класс драйвера JDBC для PostgreSQL
            '--target_table', target_table  # Аргумент: Название целевой таблицы в PostgreSQL
        ],
        conf={
            "spark.driver.memory": "1g",  # Объём памяти для драйвера Spark
            "spark.worker.memory": "1g",  # Объём памяти для воркера Spark
            "spark.worker.cores": 1,  # Количество ядер для воркера Spark
            "spark.executor.memory": "1g"  # Объём памяти для исполнительного процесса Spark
        },
        jars=JARS,  # Пути к JAR-файлам коннекторов PostgreSQL
        packages='org.apache.spark:spark-streaming-kafka-0-10_2.12:3.5.3,org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.3'
        # Дополнительные пакеты для Spark
    )

    # Определение последовательности выполнения задач: start -> spark_submit_task -> finish
    start >> spark_submit_task >> finish