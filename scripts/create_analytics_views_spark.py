#!/usr/bin/env python3
"""
create_analytics_views_spark.py
Создаёт/обновляет аналитические витрины в MySQL, используя Spark.
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import sum as _sum, count as _count

def main():
    spark = SparkSession.builder \
        .appName("create_analytics_views") \
        .getOrCreate()

    mysql_url = "jdbc:mysql://mysql_db:3306/mydb"
    mysql_user = "myuser"
    mysql_password = "myuserpwd"

    # Пример: Загружаем заказы и детали заказов
    df_orders = spark.read \
        .format("jdbc") \
        .option("url", mysql_url) \
        .option("dbtable", "orders_replica") \
        .option("user", mysql_user) \
        .option("password", mysql_password) \
        .load()

    df_order_details = spark.read \
        .format("jdbc") \
        .option("url", mysql_url) \
        .option("dbtable", "orderdetails_replica") \
        .option("user", mysql_user) \
        .option("password", mysql_password) \
        .load()

    df_join = df_orders.join(df_order_details, "order_id")

    # Cформируем агрегированную витрину - сумма и кол-во заказов на пользователя
    df_user_sales = df_join.groupBy("user_id") \
        .agg(_count("*").alias("orders_count"),
             _sum("total_price").alias("orders_total_amount"))

    # Сохраним результат как таблицу user_sales_analytics
    df_user_sales.write \
        .format("jdbc") \
        .option("url", mysql_url) \
        .option("dbtable", "user_sales_analytics") \
        .option("user", mysql_user) \
        .option("password", mysql_password) \
        .mode("overwrite") \
        .save()

    df_product_sales = df_join.groupBy("product_id") \
        .agg(
            _count("*").alias("product_orders_count"),
            _sum("quantity").alias("total_quantity_sold"),
            _sum("total_price").alias("total_revenue")
        )

    df_product_sales.write \
        .format("jdbc") \
        .option("url", mysql_url) \
        .option("dbtable", "product_sales_analytics") \
        .option("user", mysql_user) \
        .option("password", mysql_password) \
        .mode("overwrite") \
        .save()

    spark.stop()
    print("=== Analytics views created/updated successfully ===")

if __name__ == "__main__":
    main()