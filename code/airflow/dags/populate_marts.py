# Импорт необходимых модулей и классов
from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.operators.empty import EmptyOperator

from airflow.providers.mysql.hooks.mysql import MySqlHook

from scripts.helpers.airflow_common import get_connection_uri

# ================================
# Константы
# ================================

# Список аналитических витрин данных, которые будут созданы
ANALYTICAL_MARTS = ["user_activity", "average_check", "product_rating", "user_loyalty_points"]

# Путь к JAR-файлу MySQL коннектора, необходимому для подключения Spark к MySQL
JARS = "/opt/airflow/spark/jars/mysql-connector-java-8.3.0.jar"

# Путь к PySpark-скрипту, который будет выполнять создание аналитических витрин
PYSPARK_SCRIPT_PATH = '/opt/airflow/scripts/pyspark_scripts/populate_analytical_marts.py'

# ================================
# Параметры по умолчанию для DAG
# ================================

default_args = {
    'owner': 'airflow',  # Владелец DAG'а
    'depends_on_past': False,  # Не зависит от предыдущих запусков
    'start_date': datetime(year=2025, month=1, day=9),  # Дата начала выполнения DAG'а
    'email_on_failure': False,  # Не отправлять email при сбое
    'email_on_retry': False,  # Не отправлять email при повторных попытках
    'retries': 0,  # Количество попыток повторного выполнения при сбое
    'retry_delay': timedelta(minutes=5),  # Задержка между попытками повторного выполнения
    'catchup': False  # Не выполнять "догоняющие" запуски для пропущенных интервалов
}

# ================================
# Определение DAG
# ================================

with DAG(
        'create_analytical_marts',  # Идентификатор DAG'а
        default_args=default_args,  # Использование ранее определённых параметров по умолчанию
        description='Создание витрин данных в MySQL через Spark',  # Описание DAG'а
        schedule_interval=timedelta(minutes=10),  # Интервал планирования: каждые 10 минут
        concurrency=1,  # Максимальное количество задач, выполняющихся одновременно в этом DAG'е
        max_active_runs=1  # Максимальное количество активных запусков DAG'а
) as dag:
    # ================================
    # Креды и драйверы
    # ================================

    # Получение URI подключения к MySQL с использованием хука MySqlHook
    src_tgt_url = get_connection_uri(MySqlHook.get_connection('coursework_de_mysql'))

    # Определение класса драйвера JDBC для подключения к MySQL
    src_tgt_driver = 'com.mysql.cj.jdbc.Driver'

    # ================================
    # Определение задач DAG
    # ================================

    # Начальная задача DAG, не выполняет никаких действий
    start = EmptyOperator(task_id='start')

    # Конечная задача DAG, не выполняет никаких действий
    finish = EmptyOperator(task_id='finish')

    # Цикл по списку аналитических витрин для создания соответствующих задач SparkSubmitOperator
    for mart in ANALYTICAL_MARTS:
        # Определение задачи для создания конкретной витрины данных
        spark_submit_task = SparkSubmitOperator(
            task_id=f'create_mart_{mart}',  # Идентификатор задачи, уникален для каждой витрины
            application=PYSPARK_SCRIPT_PATH,  # Путь к PySpark-скрипту
            conn_id='coursework_de_spark',  # Идентификатор подключения Spark, определённый в Airflow
            application_args=[
                '--src_tgt_url', src_tgt_url,  # Аргумент: URI подключения к MySQL
                '--src_tgt_driver', src_tgt_driver,  # Аргумент: Класс драйвера JDBC
                '--target_mart', mart  # Аргумент: Название целевой витрины данных
            ],
            conf={
                "spark.driver.memory": "1g",  # Объём памяти для драйвера Spark
                "spark.worker.memory": "1g",  # Объём памяти для воркера Spark
                "spark.worker.cores": 1,  # Количество ядер для воркера Spark
                "spark.executor.memory": "1g"  # Объём памяти для исполнительного процесса Spark
            },
            jars=JARS  # Путь к JAR-файлам, необходимым для подключения Spark к MySQL
        )

        # Определение последовательности выполнения задач: start -> spark_submit_task -> finish
        start >> spark_submit_task >> finish