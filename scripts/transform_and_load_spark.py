#!/usr/bin/env python3
"""
transform_and_load_spark.py
Перенос (репликация) данных из PostgreSQL в MySQL через Spark.
В примере просто «копируем» все строки, не делая сложных трансформаций,
но при желании можно добавить и логику ETL.
"""

from pyspark.sql import SparkSession

def replicate_table(spark, table_name, pg_url, pg_user, pg_password,
                    mysql_url, mysql_user, mysql_password,
                    replica_table_name):
    """
    Обобщённая функция для чтения таблицы из PostgreSQL и записи в MySQL.
    """
    # Читаем из PostgreSQL
    df = spark.read \
        .format("jdbc") \
        .option("url", pg_url) \
        .option("dbtable", table_name) \
        .option("user", pg_user) \
        .option("password", pg_password) \
        .load()

    # Записываем в MySQL
    df.write \
        .format("jdbc") \
        .option("url", mysql_url) \
        .option("dbtable", replica_table_name) \
        .option("user", mysql_user) \
        .option("password", mysql_password) \
        .mode("overwrite") \
        .save()

def main():
    spark = SparkSession.builder \
        .appName("replicate_postgres_to_mysql") \
        .getOrCreate()

    # Подключения
    pg_url = "jdbc:postgresql://postgres_db:5432/postgres"
    pg_user = "postgres"
    pg_password = "postgres"

    mysql_url = "jdbc:mysql://mysql_db:3306/mydb"
    mysql_user = "myuser"
    mysql_password = "myuserpwd"

    # Список таблиц для репликации:
    replication_map = {
        "users": "users_replica",
        "products": "products_replica",
        "productcategories": "productcategories_replica",
        "orders": "orders_replica",
        "orderdetails": "orderdetails_replica",
    }

    for src_table, dest_table in replication_map.items():
        print(f"Replicating {src_table} -> {dest_table}")
        replicate_table(
            spark,
            table_name=src_table,
            pg_url=pg_url,
            pg_user=pg_user,
            pg_password=pg_password,
            mysql_url=mysql_url,
            mysql_user=mysql_user,
            mysql_password=mysql_password,
            replica_table_name=dest_table
        )

    spark.stop()
    print("=== Replication completed successfully ===")

if __name__ == "__main__":
    main()