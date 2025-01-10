# Импорт необходимых модулей и классов
from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.operators.empty import EmptyOperator

from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.mysql.hooks.mysql import MySqlHook

from scripts.helpers.airflow_common import get_connection_uri

# ================================
# Константы
# ================================

# Список таблиц, которые будут реплицированы из PostgreSQL в MySQL
TABLES = ["users", "products", "productcategories", "orders", "orderdetails", "reviews", "loyaltypoints"]

# Пути к JAR-файлам коннекторов PostgreSQL и MySQL, необходимые для подключения Spark к базам данных
JARS = "/opt/airflow/spark/jars/postgresql-42.2.18.jar,/opt/airflow/spark/jars/mysql-connector-java-8.3.0.jar"

# Путь к PySpark-скрипту, который выполняет репликацию данных между базами
PYSPARK_REPLICATION_SCRIPT_PATH = f'/opt/airflow/scripts/pyspark_scripts/replicate_table_by_spark.py'

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
    'retry_delay': timedelta(minutes=3),  # Задержка между попытками повторного выполнения
    'catchup': True,  # Выполнять "догоняющие" запуски для пропущенных интервалов
    'concurrency': 1  # Максимальное количество задач, выполняющихся одновременно для одного DAG'а
}

# ================================
# Определение DAG
# ================================

with DAG(
        'replicate_from_pg_to_mysql',  # Идентификатор DAG'а
        default_args=default_args,  # Использование ранее определённых параметров по умолчанию
        description='Репликация данных из PG в MySQL через Spark',  # Описание DAG'а
        schedule_interval=timedelta(minutes=10),  # Интервал планирования: каждые 10 минут
        concurrency=4,  # Максимальное количество задач, выполняющихся одновременно в этом DAG'е
        max_active_runs=1  # Максимальное количество активных запусков DAG'а одновременно
) as dag:
    # ================================
    # Креды и драйверы
    # ================================

    # Получение URI подключения к источнику данных PostgreSQL с использованием хука PostgresHook
    source_url = get_connection_uri(PostgresHook.get_connection('coursework_de_postgresql'))

    # Определение класса драйвера JDBC для подключения к PostgreSQL
    source_driver = 'org.postgresql.Driver'

    # Получение URI подключения к целевой базе данных MySQL с использованием хука MySqlHook
    target_url = get_connection_uri(MySqlHook.get_connection('coursework_de_mysql'))

    # Определение класса драйвера JDBC для подключения к MySQL
    target_driver = 'com.mysql.cj.jdbc.Driver'

    # ================================
    # Определение задач DAG
    # ================================

    # Начальная задача DAG, не выполняет никаких действий
    start = EmptyOperator(task_id='start')

    # Конечная задача DAG, не выполняет никаких действий
    finish = EmptyOperator(task_id='finish')

    # Цикл по списку таблиц для создания соответствующих задач SparkSubmitOperator
    for table in TABLES:
        # Создание задачи для репликации конкретной таблицы
        spark_submit_task = SparkSubmitOperator(
            task_id=f'replicate_{table}',  # Уникальный идентификатор задачи, основанный на названии таблицы
            application=PYSPARK_REPLICATION_SCRIPT_PATH,  # Путь к PySpark-скрипту для репликации данных
            conn_id='coursework_de_spark',  # Идентификатор подключения Spark, настроенный в Airflow
            application_args=[
                '--source_url', source_url,  # Аргумент: URI подключения к PostgreSQL
                '--source_driver', source_driver,  # Аргумент: Класс драйвера JDBC для PostgreSQL
                '--target_url', target_url,  # Аргумент: URI подключения к MySQL
                '--target_driver', target_driver,  # Аргумент: Класс драйвера JDBC для MySQL
                '--table', table  # Аргумент: Название таблицы для репликации
            ],
            conf={
                "spark.driver.memory": "1g",  # Объём памяти для драйвера Spark
                "spark.worker.memory": "1g",  # Объём памяти для воркера Spark
                "spark.worker.cores": 1,  # Количество ядер для воркера Spark
                "spark.executor.memory": "1g"  # Объём памяти для исполнительного процесса Spark
            },
            jars=JARS  # Пути к JAR-файлам коннекторов PostgreSQL и MySQL
        )

        # Определение последовательности выполнения задач: start -> spark_submit_task -> finish
        start >> spark_submit_task >> finish