#!/usr/bin/env bash
set -e

echo "=== Starting Kafka broker in the background ==="
/etc/confluent/docker/run &

sleep 5

echo "=== Launching data_generation_kafka.py ==="
python3 /app/data_generation_kafka.py

tail -f /dev/null