FROM bitnami/spark:3.5.3

USER root

RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-dev \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

USER 1001