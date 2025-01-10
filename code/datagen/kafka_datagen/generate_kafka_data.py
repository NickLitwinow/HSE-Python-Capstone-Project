import time
import json
import random
import os
import logging
from kafka import KafkaProducer

from faker import Faker


def clean_phone(phone: str) -> str:
    """Очистка телефонного номера от лишних символов и обрезка до 20 символов"""
    import re
    cleaned = re.sub(r"[^\d+]", "", phone)
    return cleaned[:20]


def generate_user_msg(fake: Faker):
    """
    Генерирует случайные данные пользователя в формате JSON.

    Args:
        fake (Faker): Экземпляр Faker, используемый для генерации случайных данных.

    Returns:
        dict: Словарь с данными пользователя.
    """
    return {
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": fake.email(),
        "phone": clean_phone(fake.phone_number()),
        "registration_date": fake.date_time_between(start_date='-1y', end_date='now').isoformat(),
        "loyalty_status": random.choice(["Gold", "Silver", "Bronze"])
    }


def main():
    """Непрерывная генерация и отправка случайных данных в Kafka топик."""
    # ================================
    # Настройка логирования
    # ================================
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # ================================
    # Получение конфигурации из переменных окружения
    # ================================
    kafka_bootstrap_servers = os.getenv("KAFKA_INTERNAL_CONNECT_PATH", "localhost:9092")
    kafka_topic = os.getenv("KAFKA_TOPIC_NAME", "users-data")
    msg_gen_period = os.getenv("KAFKA_DATAGEN_PERIOD_SECS", "1")  # По умолчанию 1 секунда

    # Проверка обязательных переменных окружения
    if not kafka_bootstrap_servers:
        logger.error("Переменная окружения 'KAFKA_INTERNAL_CONNECT_PATH' не установлена.")
        exit(1)
    if not kafka_topic:
        logger.error("Переменная окружения 'KAFKA_TOPIC_NAME' не установлена.")
        exit(1)
    try:
        msg_gen_period = float(msg_gen_period)
        if msg_gen_period <= 0:
            raise ValueError
    except ValueError:
        logger.error("Переменная окружения 'KAFKA_DATAGEN_PERIOD_SECS' должна быть положительным числом.")
        exit(1)

    # ================================
    # Инициализация Kafka Producer
    # ================================
    try:
        producer = KafkaProducer(
            bootstrap_servers=kafka_bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')  # Сериализация сообщений в JSON
        )
        logger.info(f"Подключение к Kafka серверам: {kafka_bootstrap_servers}")
        logger.info(f"Отправка сообщений в топик: {kafka_topic}")
        logger.info(f"Период генерации сообщений: {msg_gen_period} секунд(ы)")
    except Exception as e:
        logger.error(f"Не удалось подключиться к Kafka серверам: {e}")
        exit(1)

    # ================================
    # Инициализация Faker
    # ================================
    fake = Faker()
    msg_id = 1  # Счётчик сообщений

    # ================================
    # Бесконечный цикл генерации и отправки сообщений
    # ================================
    while True:
        try:
            # Генерация случайного сообщения
            msg = generate_user_msg(fake)
            # Отправка сообщения в Kafka топик
            producer.send(kafka_topic, value=msg)
            logger.info(f"Доставлено сообщение №{msg_id}: {msg}")
            # Ожидание перед отправкой следующего сообщения
            time.sleep(msg_gen_period)
            msg_id += 1
        except KeyboardInterrupt:
            # Обработка прерывания пользователем (Ctrl+C)
            logger.info("Прерывание пользователем. Завершение работы.")
            break
        except Exception as e:
            # Обработка других исключений
            logger.error(f"Ошибка при отправке сообщения: {e}")
            time.sleep(msg_gen_period)  # Ожидание перед повторной попыткой

    # ================================
    # Завершение работы Kafka Producer
    # ================================
    producer.close()
    logger.info("Kafka Producer закрыт.")


if __name__ == "__main__":
    main()