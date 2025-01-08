#!/usr/bin/env python3
"""
kafka_to_postgres.py
Чтение данных из Kafka-топика и запись их в PostgreSQL.
Пример - batch-режим (startingOffsets='earliest').
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructType, StructField, StringType, TimestampType

def main():
    spark = SparkSession \
        .builder \
        .appName("kafka_to_postgres_batch") \
        .getOrCreate()

    # Адрес Kafka
    kafka_bootstrap = "kafka:9092"
    topic_name = "my_topic"

    # Читаем из Kafka (batch)
    df = spark.read \
        .format("kafka") \
        .option("kafka.bootstrap.servers", kafka_bootstrap) \
        .option("subscribe", topic_name) \
        .option("startingOffsets", "earliest") \
        .load()
    df_string = df.selectExpr("CAST(value AS STRING) as json_string")

    # Определяем схему для парсинга JSON
    json_schema = StructType([
        StructField("event_type", StringType()),
        StructField("user_id", StringType()),
        StructField("timestamp", StringType()),
        StructField("page_url", StringType()),
        StructField("ip_address", StringType())
    ])

    df_parsed = df_string.select(
        from_json(col("json_string"), json_schema).alias("data")
    ).select("data.*")

    from pyspark.sql.functions import to_timestamp
    df_final = df_parsed.withColumn(
        "timestamp",
        to_timestamp(col("timestamp"), "yyyy-MM-dd'T'HH:mm:ss.SSSSSS")
    )

    # Пишем в PostgreSQL
    df_final.write \
        .format("jdbc") \
        .option("url", "jdbc:postgresql://postgres_db:5432/postgres") \
        .option("dbtable", "kafka_events") \
        .option("user", "postgres") \
        .option("password", "postgres") \
        .mode("append") \
        .save()

    spark.stop()
    print("=== Kafka -> PostgreSQL batch load completed ===")

if __name__ == "__main__":
    main()