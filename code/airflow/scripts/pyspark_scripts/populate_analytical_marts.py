import argparse
from pyspark.sql import SparkSession
from pyspark.sql.functions import desc


def create_user_activity_view(src_tgt_url: str, src_tgt_driver: str, tgt_mart_name: str):
    """
    Создает или перезаписывает витрину активности пользователей с разбивкой по статусу заказа.

    Args:
        src_tgt_url (str): URL для подключения к источнику и приемнику данных.
        src_tgt_driver (str): Класс драйвера JDBC для подключения к СУБД.
        tgt_mart_name (str): Имя целевой витрины данных.
    """
    # ================================
    # Создание Spark сессии
    # ================================
    spark = (
        SparkSession.builder
        .appName(f"Create_mart_{tgt_mart_name}")  # Название приложения Spark
        .getOrCreate()  # Создание или получение существующей Spark сессии
    )

    # ================================
    # Чтение данных из "STG" слоя
    # ================================
    # Чтение таблицы "users" из базы данных через JDBC
    users_df = (
        spark.read
        .format("jdbc")  # Формат источника данных – JDBC
        .option("url", src_tgt_url)  # URL подключения к базе данных
        .option("driver", src_tgt_driver)  # Драйвер JDBC для подключения
        .option("dbtable", "users")  # Имя таблицы для чтения
        .load()  # Загрузка данных в DataFrame
    )

    # Чтение таблицы "orders" из базы данных через JDBC
    orders_df = (
        spark.read
        .format("jdbc")
        .option("url", src_tgt_url)
        .option("driver", src_tgt_driver)
        .option("dbtable", "orders")
        .load()
    )

    # ================================
    # Создание витрины активности пользователей
    # ================================
    user_activity_df = (
        orders_df.join(users_df, "user_id")  # Объединение таблиц по полю "user_id"
        .groupBy("user_id", "first_name", "last_name", "status")  # Группировка по пользователям и статусу заказа
        .agg({"order_id": "count", "total_amount": "sum"})  # Агрегация: количество заказов и сумма потраченных средств
        .withColumnRenamed("count(order_id)", "order_count")  # Переименование столбца
        .withColumnRenamed("sum(total_amount)", "total_spent")  # Переименование столбца
    )

    # ================================
    # Запись витрины в приемник
    # ================================
    (
        user_activity_df.write
        .format("jdbc")  # Формат источника данных – JDBC
        .option("url", src_tgt_url)  # URL подключения к базе данных
        .option("driver", src_tgt_driver)  # Драйвер JDBC для подключения
        .option("dbtable", f"mart_{tgt_mart_name}")  # Имя целевой таблицы для записи
        .mode("overwrite")  # Режим записи: перезапись существующей таблицы
        .save()  # Сохранение данных в целевой таблице
    )

    # ================================
    # Остановка Spark сессии
    # ================================
    spark.stop()  # Завершение работы Spark сессии


def create_product_rating_view(src_tgt_url: str, src_tgt_driver: str, tgt_mart_name: str):
    """
    Создает или перезаписывает витрину рейтингов продуктов с разбивкой по названию продукта.

    Args:
        src_tgt_url (str): URL для подключения к источнику и приемнику данных.
        src_tgt_driver (str): Класс драйвера JDBC для подключения к СУБД.
        tgt_mart_name (str): Имя целевой витрины данных.
    """
    # ================================
    # Создание Spark сессии
    # ================================
    spark = (
        SparkSession.builder
        .appName(f"Create_mart_{tgt_mart_name}")
        .getOrCreate()
    )

    # ================================
    # Чтение данных из "STG" слоя
    # ================================
    # Чтение таблицы "products" из базы данных через JDBC
    products_df = (
        spark.read
        .format("jdbc")
        .option("url", src_tgt_url)
        .option("driver", src_tgt_driver)
        .option("dbtable", "products")
        .load()
    )

    # Чтение таблицы "reviews" из базы данных через JDBC
    reviews_df = (
        spark.read
        .format("jdbc")
        .option("url", src_tgt_url)
        .option("driver", src_tgt_driver)
        .option("dbtable", "reviews")
        .load()
    )

    # ================================
    # Создание витрины рейтингов продуктов
    # ================================
    product_rating_df = (
        products_df.join(reviews_df, "product_id")  # Объединение таблиц по полю "product_id"
        .groupBy("product_id", "name")  # Группировка по продуктам
        .agg({"rating": "avg"})  # Агрегация: средний рейтинг
        .withColumnRenamed("avg(rating)", "rating")  # Переименование столбца
        .orderBy(desc("rating"))  # Сортировка по убыванию рейтинга
    )

    # ================================
    # Запись витрины в приемник
    # ================================
    (
        product_rating_df.write
        .format("jdbc")
        .option("url", src_tgt_url)
        .option("driver", src_tgt_driver)
        .option("dbtable", f"mart_{tgt_mart_name}")
        .mode("overwrite")
        .save()
    )

    # ================================
    # Остановка Spark сессии
    # ================================
    spark.stop()


def create_user_loyalty_points_view(src_tgt_url: str, src_tgt_driver: str, tgt_mart_name: str):
    """
    Создает или перезаписывает витрину бонусных баллов пользователей.

    Args:
        src_tgt_url (str): URL для подключения к источнику и приемнику данных.
        src_tgt_driver (str): Класс драйвера JDBC для подключения к СУБД.
        tgt_mart_name (str): Имя целевой витрины данных.
    """
    # ================================
    # Создание Spark сессии
    # ================================
    spark = (
        SparkSession.builder
        .appName(f"Create_mart_{tgt_mart_name}")
        .getOrCreate()
    )

    # ================================
    # Чтение данных из "STG" слоя
    # ================================
    # Чтение таблицы "users" из базы данных через JDBC
    users_df = (
        spark.read
        .format("jdbc")
        .option("url", src_tgt_url)
        .option("driver", src_tgt_driver)
        .option("dbtable", "users")
        .load()
    )

    # Чтение таблицы "loyaltypoints" из базы данных через JDBC
    loyaltypoints_df = (
        spark.read
        .format("jdbc")
        .option("url", src_tgt_url)
        .option("driver", src_tgt_driver)
        .option("dbtable", "loyaltypoints")
        .load()
    )

    # ================================
    # Создание витрины бонусных баллов пользователей
    # ================================
    user_loyalty_points_df = (
        users_df.join(loyaltypoints_df, "user_id")  # Объединение таблиц по полю "user_id"
        .groupBy("user_id", "first_name", "last_name",
                 "loyalty_status")  # Группировка по пользователям и статусу лояльности
        .agg({"points": "sum"})  # Агрегация: сумма бонусных баллов
        .withColumnRenamed("sum(points)", "total_loyalty_points")  # Переименование столбца
        .orderBy(desc("total_loyalty_points"))  # Сортировка по убыванию суммы бонусных баллов
    )

    # ================================
    # Запись витрины в приемник
    # ================================
    (
        user_loyalty_points_df.write
        .format("jdbc")
        .option("url", src_tgt_url)
        .option("driver", src_tgt_driver)
        .option("dbtable", f"mart_{tgt_mart_name}")
        .mode("overwrite")
        .save()
    )

    # ================================
    # Остановка Spark сессии
    # ================================
    spark.stop()


def create_average_check_view(src_tgt_url: str, src_tgt_driver: str, tgt_mart_name: str):
    """
    Создает или перезаписывает витрину среднего чека с разбивкой по статусу заказа и статусу лояльности.

    Args:
        src_tgt_url (str): URL для подключения к источнику и приемнику данных.
        src_tgt_driver (str): Класс драйвера JDBC для подключения к СУБД.
        tgt_mart_name (str): Имя целевой витрины данных.
    """
    # ================================
    # Создание Spark сессии
    # ================================
    spark = (
        SparkSession.builder
        .appName(f"Create_mart_{tgt_mart_name}")
        .getOrCreate()
    )

    # ================================
    # Чтение данных из "STG" слоя
    # ================================
    # Чтение таблицы "orders" из базы данных через JDBC
    orders_df = (
        spark.read
        .format("jdbc")
        .option("url", src_tgt_url)
        .option("driver", src_tgt_driver)
        .option("dbtable", "orders")
        .load()
    )

    # Чтение таблицы "users" из базы данных через JDBC
    users_df = (
        spark.read
        .format("jdbc")
        .option("url", src_tgt_url)
        .option("driver", src_tgt_driver)
        .option("dbtable", "users")
        .load()
    )

    # ================================
    # Создание витрины среднего чека
    # ================================
    average_check_df = (
        orders_df.join(users_df, "user_id")  # Объединение таблиц по полю "user_id"
        .groupBy("status", "loyalty_status")  # Группировка по статусу заказа и статусу лояльности
        .agg({"total_amount": "avg"})  # Агрегация: средний чек
        .withColumnRenamed("avg(total_amount)", "average_check")  # Переименование столбца
    )

    # ================================
    # Запись витрины в приемник
    # ================================
    (
        average_check_df.write
        .format("jdbc")
        .option("url", src_tgt_url)
        .option("driver", src_tgt_driver)
        .option("dbtable", f"mart_{tgt_mart_name}")
        .mode("overwrite")
        .save()
    )

    # ================================
    # Остановка Spark сессии
    # ================================
    spark.stop()


def main():
    """
    Точка входа. Парсит аргументы командной строки и запускает создание или перезапись соответствующей витрины.

    Args:
        --src_tgt_url (str): URL для подключения к источнику и приемнику данных.
        --src_tgt_driver (str): Класс драйвера JDBC для подключения к СУБД.
        --target_mart (str): Имя целевой витрины данных. Возможные значения:
                               'user_activity', 'product_rating', 'average_check', 'user_loyalty_points'.
    """
    # Создание парсера аргументов командной строки
    parser = argparse.ArgumentParser(description="Создание аналитических витрин данных с использованием PySpark.")

    # Добавление аргумента --src_tgt_url (обязательный)
    parser.add_argument('--src_tgt_url', type=str, required=True,
                        help='URL для подключения к источнику и приемнику данных.')

    # Добавление аргумента --src_tgt_driver (обязательный)
    parser.add_argument("--src_tgt_driver", type=str, required=True,
                        help='Класс драйвера JDBC для подключения к СУБД.')

    # Добавление аргумента --target_mart (обязательный, с ограничениями на выбор)
    parser.add_argument('--target_mart', type=str, required=True,
                        choices=['user_activity', 'product_rating', 'average_check', "user_loyalty_points"],
                        help='Имя целевой витрины данных.')

    # Парсинг аргументов командной строки
    args = parser.parse_args()

    # Вызов соответствующей функции в зависимости от выбранной витрины
    if args.target_mart == "user_activity":
        create_user_activity_view(args.src_tgt_url, args.src_tgt_driver, args.target_mart)
    elif args.target_mart == "product_rating":
        create_product_rating_view(args.src_tgt_url, args.src_tgt_driver, args.target_mart)
    elif args.target_mart == "average_check":
        create_average_check_view(args.src_tgt_url, args.src_tgt_driver, args.target_mart)
    elif args.target_mart == "user_loyalty_points":
        create_user_loyalty_points_view(args.src_tgt_url, args.src_tgt_driver, args.target_mart)


if __name__ == "__main__":
    main()