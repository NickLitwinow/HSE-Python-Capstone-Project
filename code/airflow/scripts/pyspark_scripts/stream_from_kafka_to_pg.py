import argparse
import logging
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, TimestampType


def stream_kafka_to_postgres(kafka_bootstrap_servers: str, kafka_topic: str, target_url: str, target_driver: str, target_table: str):
    """
    Читает данные из Kafka и записывает их в PostgreSQL.

    Args:
        kafka_bootstrap_servers (str): Адреса Kafka bootstrap servers.
        kafka_topic (str): Название Kafka топика.
        target_url (str): URL для подключения к приемнику.
        target_driver (str): Драйвер для подключения к приемнику.
        target_table (str): Имя таблицы в приемнике.
    """
    # ================================
    # Настройка логирования
    # ================================
    logging.basicConfig(level=logging.INFO)
    logging.info(f"Запуск стриминга из Kafka топика '{kafka_topic}' в PostgreSQL таблицу '{target_table}'.")

    # ================================
    # Определение схемы данных
    # ================================
    schema = StructType([
        StructField("first_name", StringType(), True),
        StructField("last_name", StringType(), True),
        StructField("email", StringType(), True),
        StructField("phone", StringType(), True),
        StructField("registration_date", TimestampType(), True),
        StructField("loyalty_status", StringType(), True)
    ])

    # ================================
    # Создание Spark-сессии
    # ================================
    spark = SparkSession.builder.appName("KafkaToPG").getOrCreate()

    try:
        # ================================
        # Чтение данных из Kafka
        # ================================
        logging.info("Чтение данных из Kafka...")
        df = (
            spark.readStream
            .format("kafka")  # Указание формата источника данных – Kafka
            .option("kafka.bootstrap.servers", kafka_bootstrap_servers)  # Адреса Kafka bootstrap servers
            .option("subscribe", kafka_topic)  # Название Kafka топика для подписки
            .load()  # Загрузка данных в DataFrame
        )

        # ================================
        # Преобразование данных
        # ================================
        logging.info("Преобразование данных...")
        df = (
            df.selectExpr("CAST(value AS STRING)")  # Преобразование байтового значения в строку
            .select(from_json(col("value"), schema).alias("data"))  # Парсинг JSON-строки в структурированные данные по заданной схеме
            .select("data.*")  # Выбор всех полей из вложенного объекта "data"
        )

        # ================================
        # Запись данных в PostgreSQL
        # ================================
        logging.info("Запуск записи данных в PostgreSQL...")
        query = (
            df.writeStream
            .foreachBatch(
                lambda batch_df, batch_id:
                batch_df.write
                .format("jdbc")  # Указание формата записи – JDBC
                .option("url", target_url)  # URL подключения к PostgreSQL
                .option("driver", target_driver)  # Класс драйвера JDBC для PostgreSQL
                .option("dbtable", target_table)  # Название целевой таблицы в PostgreSQL
                .mode("append")  # Режим записи: добавление данных
                .save()  # Сохранение данных в целевой таблице
            )
            .start()  # Запуск стриминга
        )

        # ================================
        # Ожидание завершения стриминга
        # ================================
        logging.info("Ожидание завершения стриминга...")
        query.awaitTermination()  # Ожидание завершения стриминга
    except Exception as e:
        # ================================
        # Обработка исключений
        # ================================
        logging.error(f"Ошибка во время стриминга: {e}")
    finally:
        # ================================
        # Остановка Spark-сессии
        # ================================
        logging.info("Остановка Spark-сессии.")
        spark.stop()  # Завершение работы Spark-сессии


def main():
    """
    Точка входа. Парсит аргументы и запускает стриминг данных из Kafka в СУБД.

    Args:
        --kafka_bootstrap_servers (str): Адреса Kafka bootstrap servers.
        --kafka_topic (str): Название Kafka топика.
        --target_url (str): URL для подключения к приемнику.
        --target_driver (str): Драйвер для подключения к приемнику.
        --target_table (str): Имя таблицы в приемнике.
    """
    # ================================
    # Парсинг аргументов командной строки
    # ================================
    parser = argparse.ArgumentParser(description="Стриминговое чтение пользователей из Kafka и запись в Postgres.")
    parser.add_argument("--kafka_bootstrap_servers", type=str, required=True, help="Адреса Kafka bootstrap servers.")
    parser.add_argument("--kafka_topic", type=str, required=True, help="Название Kafka топика.")
    parser.add_argument("--target_url", type=str, required=True, help="URL для подключения к приемнику.")
    parser.add_argument("--target_driver", type=str, required=True, help="Драйвер для подключения к приемнику.")
    parser.add_argument("--target_table", type=str, required=True, help="Имя таблицы в приемнике.")

    args = parser.parse_args()  # Считывание и парсинг аргументов

    # ================================
    # Запуск процесса стриминга
    # ================================
    stream_kafka_to_postgres(
        kafka_bootstrap_servers=args.kafka_bootstrap_servers,
        kafka_topic=args.kafka_topic,
        target_url=args.target_url,
        target_driver=args.target_driver,
        target_table=args.target_table
    )


if __name__ == "__main__":
    main()  # Вызов функции main при запуске скрипта напрямую