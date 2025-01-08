#!/usr/bin/env bash
set -e

echo "=== Init Airflow Connections ==="

# Удаляем, если существуют, чтобы избежать ошибки "Connection already exists"
airflow connections delete 'postgres_default' || true
airflow connections delete 'mysql_default' || true
airflow connections delete 'spark_default' || true
airflow connections delete 'kafka_default' || true

# Создаём Postgres connection
airflow connections add 'postgres_default' \
    --conn-uri 'postgresql+psycopg2://postgres:postgres@postgres_db:5432/postgres'

# Создаём MySQL connection
airflow connections add 'mysql_default' \
    --conn-uri 'mysql+pymysql://myuser:myuserpwd@mysql_db:3306/mydb'

# Создаём Spark connection
airflow connections add 'spark_default' \
    --conn-type 'spark' \
    --conn-host 'spark' \
    --conn-port '7077' \
    --conn-extra '{"queue": "default"}'

# Создаём Kafka connection
airflow connections add 'kafka_default' \
    --conn-type 'kafka' \
    --conn-host 'kafka' \
    --conn-port '9092' \
    --conn-extra '{"schema.registry.url": "http://kafka:8081"}'

echo "=== Airflow Connections created successfully ==="