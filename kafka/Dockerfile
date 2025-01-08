FROM confluentinc/cp-kafka:latest

USER root

RUN pip3 install kafka-python faker

COPY data_generation_kafka.py /app/data_generation_kafka.py
COPY docker-entrypoint.sh /docker-entrypoint.sh

RUN chmod +x /docker-entrypoint.sh

USER root

ENTRYPOINT ["/docker-entrypoint.sh"]