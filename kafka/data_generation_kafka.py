#!/usr/bin/env python3

import json
import time
import random
from datetime import datetime
from kafka import KafkaProducer
from faker import Faker

fake = Faker()

def generate_event():
    """Генерируем пример события, которое хотим отправить в Kafka."""
    event_types = ["page_view", "click", "purchase", "login", "logout"]
    event_type = random.choice(event_types)
    return {
        "event_type": event_type,
        "user_id": random.randint(1, 1000),
        "timestamp": datetime.now().isoformat(),
        "page_url": fake.uri(),
        "ip_address": fake.ipv4()
    }

def main():
    producer = None
    try:
        # Внутри docker-compose Kafka доступна по хосту 'kafka:9092'
        producer = KafkaProducer(
            bootstrap_servers=['kafka:9092'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

        topic_name = "my_topic"

        print("=== Starting Kafka data generation ===")

        # Генерируем данные в бесконечном цикле
        while True:
            event = generate_event()
            producer.send(topic_name, value=event)
            print(f"Sent event: {event}")
            time.sleep(2)  # Каждые 2 секунды отправляем событие

    except Exception as e:
        print(f"Error in Kafka Producer: {e}")

    finally:
        if producer:
            producer.flush()
            producer.close()

if __name__ == "__main__":
    main()