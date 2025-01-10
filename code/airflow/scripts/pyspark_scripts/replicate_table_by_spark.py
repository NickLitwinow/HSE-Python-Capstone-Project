import argparse
from pyspark.sql import SparkSession
import logging

def replicate_table(source_url: str, source_driver: str, target_url: str, target_driver: str, table: str):
    """
    Реплицирует таблицу из источника в приемник, учитывая возможные внешние ключи.

    Args:
        source_url (str): URL для подключения к источнику данных.
        source_driver (str): Класс драйвера JDBC для подключения к источнику данных.
        target_url (str): URL для подключения к приемнику данных.
        target_driver (str): Класс драйвера JDBC для подключения к приемнику данных.
        table (str): Имя таблицы для репликации.
    """
    # ================================
    # Настройка логирования
    # ================================
    logging.basicConfig(
        level=logging.INFO,  # Уровень логирования: INFO (информационные сообщения и выше)
        format='%(asctime)s - %(levelname)s - %(message)s'  # Формат сообщения логов
    )
    logger = logging.getLogger(__name__)  # Получение объекта логгера для текущего модуля

    logger.info(f"Начинается репликация таблицы '{table}' из источника в приемник.")

    try:
        # ================================
        # Создание Spark сессии
        # ================================
        logger.info("Создание Spark сессии.")
        spark = (
            SparkSession.builder
            .appName(f"replicate_table_{table}")  # Название приложения Spark, включающее имя таблицы
            .getOrCreate()  # Создание новой или получение существующей Spark сессии
        )

        # ================================
        # Чтение данных из источника
        # ================================
        logger.info(f"Чтение данных из таблицы '{table}' из источника.")
        source_df = (
            spark.read
            .format("jdbc")  # Использование JDBC формата для чтения данных
            .option("driver", source_driver)  # Указание класса драйвера JDBC для источника
            .option("url", source_url)  # URL подключения к источнику данных
            .option("dbtable", table)  # Имя таблицы для чтения
            .load()  # Загрузка данных в DataFrame
        )

        # ================================
        # Запись данных в приемник
        # ================================
        logger.info(f"Запись данных в таблицу '{table}' в приемнике.")
        (
            source_df.write
            .format("jdbc")  # Использование JDBC формата для записи данных
            .option("driver", target_driver)  # Указание класса драйвера JDBC для приемника
            .option("url", target_url)  # URL подключения к приемнику данных
            .option("dbtable", table)  # Имя таблицы для записи
            .mode("overwrite")  # Режим записи: перезапись существующей таблицы
            .save()  # Сохранение данных в целевой таблице
        )

        logger.info(f"Репликация таблицы '{table}' завершена успешно.")

    except Exception as e:
        # ================================
        # Обработка исключений
        # ================================
        logger.error(f"Ошибка при репликации таблицы '{table}': {e}", exc_info=True)
        raise  # Повторное выбрасывание исключения для дальнейшей обработки

    finally:
        # ================================
        # Остановка Spark сессии
        # ================================
        logger.info("Остановка Spark сессии.")
        spark.stop()  # Завершение работы Spark сессии

def main():
    """
    Точка входа. Парсит аргументы командной строки и запускает репликацию указанной таблицы.

    Args:
        --source_url (str): URL для подключения к источнику данных.
        --source_driver (str): Класс драйвера JDBC для подключения к источнику данных.
        --target_url (str): URL для подключения к приемнику данных.
        --target_driver (str): Класс драйвера JDBC для подключения к приемнику данных.
        --table (str): Имя таблицы на источнике для репликации.
    """
    # ================================
    # Парсинг аргументов командной строки
    # ================================
    parser = argparse.ArgumentParser(description="Репликация таблицы из источника в приемник с использованием Spark.")
    parser.add_argument("--source_url", type=str, required=True, help="URL для подключения к источнику данных.")
    parser.add_argument("--source_driver", type=str, required=True, help="Класс драйвера JDBC для подключения к источнику данных.")
    parser.add_argument("--target_url", type=str, required=True, help="URL для подключения к приемнику данных.")
    parser.add_argument("--target_driver", type=str, required=True, help="Класс драйвера JDBC для подключения к приемнику данных.")
    parser.add_argument("--table", type=str, required=True, help="Имя таблицы на источнике для репликации.")

    args = parser.parse_args()  # Считывание и парсинг аргументов

    # ================================
    # Запуск процесса репликации
    # ================================
    replicate_table(
        source_url=args.source_url,
        source_driver=args.source_driver,
        target_url=args.target_url,
        target_driver=args.target_driver,
        table=args.table
    )

if __name__ == "__main__":
    main()  # Вызов функции main при запуске скрипта