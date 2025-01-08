# Базируемся на официальном образе Airflow
FROM apache/airflow:2.6.2

USER root

# Устанавливаем системные зависимости, включая Java и procps
RUN apt-get update && apt-get install -y \
    libpq-dev \
    build-essential \
    python3-dev \
    openjdk-11-jdk \
    ant \
    procps \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем JAVA_HOME и добавляем Java в PATH
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-arm64
ENV PATH=$JAVA_HOME/bin:$PATH

# Устанавливаем Spark
ENV SPARK_VERSION=3.5.3
ENV HADOOP_VERSION=3

RUN wget https://downloads.apache.org/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz \
    && tar xvf spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz -C /opt/ \
    && mv /opt/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} /opt/spark \
    && rm spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz

ENV SPARK_HOME=/opt/spark
ENV PATH=$SPARK_HOME/bin:$PATH

# Скопируем requirements.txt
COPY requirements.txt /tmp/requirements.txt

# Копируем скрипты (init_airflow_connections.sh и др.) в /opt/airflow/scripts
COPY scripts /opt/airflow/scripts
RUN chmod +x /opt/airflow/scripts/init_airflow_connections.sh

# Переключаемся на пользователя airflow
USER airflow

# Установим Python-пакеты
RUN pip install --no-cache-dir -r /tmp/requirements.txt
