
# Python для инженерии данных: Итоговый проект

## Оглавление

1. [Введение](#введение)
2. [Требования](#требования)
3. [Структура проекта](#структура-проекта)
4. [Установка и запуск](#установка-и-запуск)
5. [Описание компонентов](#описание-компонентов)
    - [PostgreSQL](#postgresql)
    - [MySQL](#mysql)
    - [Kafka и Zookeeper](#kafka-и-zookeeper)
    - [Spark](#spark)
    - [Airflow](#airflow)
6. [Генерация данных](#генерация-данных)
7. [Репликация данных](#репликация-данных)
8. [Создание аналитических витрин](#создание-аналитических-витрин)
9. [Дополнительное задание: Стриминг через Kafka](#дополнительное-задание-стриминг-через-kafka)
10. [Требования к идемпотентности](#требования-к-идемпотентности)
11. [Заключение](#заключение)

## Введение

Этот проект представляет собой комплексное решение для обработки данных с использованием технологий Python, Airflow, Spark, Kafka, PostgreSQL и MySQL. Цель проекта — продемонстрировать навыки разработки пайплайнов для репликации данных, создания аналитических витрин и обработки стриминговых данных.

## Требования

Перед началом работы убедитесь, что на вашей машине установлены следующие инструменты:

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)
- [Git](https://git-scm.com/downloads)

## Структура проекта

Проект организован следующим образом:

```
.
├── docker-compose.yml
├── README.md
├── airflow
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── scripts
│   │   └── init_airflow_connections.sh
│   └── dags
│       ├── dag_replication.py
│       ├── dag_kafka_stream.py
│       └── dag_analytics.py
├── db
│   ├── init_postgres.sql
│   ├── init_mysql.sql
│   └── data_generation_postgres.py
├── kafka
│   ├── Dockerfile
│   ├── data_generation_kafka.py
│   └── docker-entrypoint.sh
├── spark
│   ├── master
│   │   └── Dockerfile
│   ├── worker
│   │   └── Dockerfile
│   └── requirements.txt
└── scripts
    ├── transform_and_load_spark.py
    ├── kafka_to_postgres.py
    └── create_analytics_views_spark.py
```

## Установка и запуск

1. **Клонируйте репозиторий:**

    ```bash
    git clone https://github.com/ваш_репозиторий/HSE_Python_Final.git
    cd HSE_Python_Final
    ```

2. **Запустите Docker Compose:**

    ```bash
    docker-compose up --build -d
    ```

    Это поднимет все сервисы: PostgreSQL, MySQL, Zookeeper, Kafka, Spark Master и Worker, Airflow (инициализация, вебсервер и планировщик).

3. **Проверьте статус контейнеров:**

    ```bash
    docker-compose ps
    ```

4. **Дождитесь полной инициализации:**

    Убедитесь, что все контейнеры находятся в состоянии `healthy` или `running`. Это может занять несколько минут.

## Описание компонентов

### PostgreSQL

- **Контейнер:** `postgres_db`
- **Порты:** `5432:5432`
- **Данные:** Хранятся в volume `postgres_data`
- **Инициализация:** Скрипт `init_postgres.sql` создаёт необходимые таблицы

### MySQL

- **Контейнер:** `mysql_db`
- **Порты:** `3306:3306`
- **Данные:** Хранятся в volume `mysql_data`
- **Инициализация:** Скрипт `init_mysql.sql` создаёт реплицируемые таблицы

### Kafka и Zookeeper

- **Zookeeper Контейнер:** `zookeeper`
- **Kafka Контейнер:** `kafka`
- **Порты:** `2181:2181` для Zookeeper, `9092:9092` и `9093:9093` для Kafka
- **Генерация данных:** Скрипт `data_generation_kafka.py` отправляет события в топик `my_topic`

### Spark

- **Spark Master Контейнер:** `spark_master`
- **Spark Worker Контейнер:** `spark_worker`
- **Порты:** `8081:8081` для веб-интерфейса Spark Master
- **Скрипты:** Хранятся в `./scripts` и доступны внутри контейнеров Spark

### Airflow

- **Airflow Контейнеры:**
    - `airflow_init` — инициализация базы данных и создание подключений
    - `airflow_webserver` — веб-интерфейс Airflow на порту `8080:8080`
    - `airflow_scheduler` — планировщик задач Airflow
- **Volume:** `airflow_logs` для логов и `airflow_plugins` для плагинов
- **Инициализация:** Скрипт `init_airflow_connections.sh` создаёт необходимые подключения и пользователя admin

## Генерация данных

### PostgreSQL

Скрипт `db/data_generation_postgres.py` генерирует тестовые данные для таблиц `users`, `products`, `orders` и `orderdetails` в PostgreSQL. Он идемпотентен: при повторном запуске данные не дублируются.

### Kafka

Скрипт `kafka/data_generation_kafka.py` генерирует события пользовательской активности и отправляет их в Kafka-топик `my_topic`. Скрипт запускается автоматически при старте контейнера Kafka.

## Репликация данных

Используется Airflow DAG `dag_replication.py`, который выполняет следующие шаги:

1. Извлечение данных из PostgreSQL.
2. Трансформация данных с помощью Spark.
3. Загрузка данных в MySQL.

## Создание аналитических витрин

Airflow DAG `dag_analytics.py` запускает скрипт `scripts/create_analytics_views_spark.py`, который:

1. Загружает данные из MySQL.
2. Выполняет агрегации и объединения для создания аналитических витрин.
3. Сохраняет результаты обратно в MySQL.

### Примеры витрин

- **User Sales Analytics:** Анализ поведения пользователей, включая количество заказов и общую сумму.
- **Product Sales Analytics:** Анализ продаж товаров, включая количество заказов, количество проданных единиц и общий доход.

## Дополнительное задание: Стриминг через Kafka

Airflow DAG `dag_kafka_stream.py` запускает скрипт `scripts/kafka_to_postgres.py`, который:

1. Читает данные из Kafka-топика `my_topic`.
2. Обрабатывает данные с помощью Spark.
3. Загружает обработанные данные в таблицу `kafka_events` в PostgreSQL.

## Требования к идемпотентности

Проект реализует идемпотентность на нескольких уровнях:

- **Инициализация баз данных:** Скрипты `init_postgres.sql` и `init_mysql.sql` используют команды `CREATE TABLE IF NOT EXISTS`, чтобы избежать дублирования при повторном запуске.
- **Генерация данных:** Скрипт `data_generation_postgres.py` проверяет наличие данных перед генерацией.
- **Airflow Connections:** Скрипт `init_airflow_connections.sh` удаляет существующие подключения перед созданием новых.
- **Запись данных в Spark:** Используется режим `overwrite` или `append`, чтобы избежать дублирования данных при многократном запуске задач.

## Заключение

Этот проект демонстрирует полный цикл обработки данных с использованием современных инструментов и технологий. Он включает в себя генерацию данных, их репликацию, создание аналитических витрин и обработку стриминговых данных. Все компоненты интегрированы и управляются с помощью Docker Compose, что обеспечивает удобство развертывания и масштабируемость решения.
