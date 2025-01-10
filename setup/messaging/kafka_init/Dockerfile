FROM confluentinc/cp-kafka:7.8.0

USER root

COPY kafka_init.sh /usr/bin/kafka_init.sh
RUN ls -l /usr/bin/kafka_init.sh

ENTRYPOINT ["/usr/bin/kafka_init.sh"]