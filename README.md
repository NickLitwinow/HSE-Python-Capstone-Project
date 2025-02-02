# Final Python Project

This project is a complete data engineering and analytics solution that integrates multiple modern technologies to automate data ingestion, processing, replication, and analytics. The system leverages containerization and orchestration to seamlessly manage complex data pipelines.

## Table of Contents

- [Technology Stack](#technology-stack)
- [Automation and Containers](#automation-and-containers)
- [Database Entities](#database-entities)
- [Service Configuration and Access](#service-configuration-and-access)
- [Data Generation Parameters](#data-generation-parameters)
- [Data Replication and Streaming](#data-replication-and-streaming)
- [Analytical Data Marts](#analytical-data-marts)
- [Project Structure](#project-structure)
- [Deployment](#deployment)
- [Usage](#usage)
- [License](#license)

## Technology Stack

- **Airflow**: Orchestrates ETL jobs, replication, and streaming pipelines.
- **Spark**: Processes and aggregates data.
- **PostgreSQL** and **MySQL**: Serve as relational databases for storing source and processed data.
- **Kafka**: Acts as the messaging broker for real-time event streaming.
- **Python**: Used for data generation scripts for PostgreSQL and Kafka.
- **Docker**: Containerizes all services to simplify deployment and scalability.

## Automation and Containers

The system consists of 14 Docker containers:
1. **PostgreSQL** – Primary database.
2. **MySQL** – Secondary database.
3. **Spark Master** – Central coordinator for Spark jobs.
4. **Spark Workers (3 instances)** – Execute Spark tasks.
5. **PostgreSQL Data Generator (`pg_datagen`)** – Generates synthetic data for PostgreSQL.
6. **Kafka Data Generator (`kafka_datagen`)** – Generates JSON events for Kafka.
7. **Kafka Init** – Initializes Kafka topics.
8. **Kafka** – Messaging broker.
9. **Zookeeper** – Manages Kafka cluster coordination.
10. **Airflow Init** – Sets up initial Airflow configuration.
11. **Airflow Scheduler** – Schedules DAG runs.
12. **Airflow Webserver** – Provides the UI for managing workflows.

All containers are based on open-source Docker images, automatically configured via a centralized `.env` file that defines login credentials, ports, data generation settings, and other configuration parameters. Healthchecks ensure that each container is properly initialized before starting dependent services.

## Database Entities

### Users
- **user_id (PK)**: Unique user identifier.
- **first_name**: User's first name.
- **last_name**: User's last name.
- **email**: Email address (unique).
- **phone**: Phone number.
- **registration_date**: Registration date.
- **loyalty_status**: Loyalty tier (`Gold`, `Silver`, `Bronze`).

### Product Categories
- **category_id (PK)**: Unique category identifier.
- **name**: Category name.
- **parent_category_id (FK)**: Parent category reference.

### Products
- **product_id (PK)**: Unique product identifier.
- **name**: Product name.
- **description**: Product description.
- **category_id (FK)**: Product category.
- **price**: Product price.
- **stock_quantity**: Quantity available in stock.
- **creation_date**: Date the product was added.

### Orders
- **order_id (PK)**: Unique order identifier.
- **user_id (FK)**: User who placed the order.
- **order_date**: Order date.
- **total_amount**: Total order value.
- **status**: Order status (e.g., `Pending`, `Completed`).
- **delivery_date**: Delivery date.

### Order Details
- **order_detail_id (PK)**: Unique identifier for order details.
- **order_id (FK)**: Reference to the order.
- **product_id (FK)**: Reference to the product.
- **quantity**: Number of units ordered.
- **price_per_unit**: Price per unit.
- **total_price**: Total price for the line item.

### Reviews
- **review_id (PK)**: Unique review identifier.
- **user_id (FK)**: User who wrote the review.
- **product_id (FK)**: Product reviewed.
- **rating**: Product rating (1 to 5).
- **review_text**: Review text.
- **created_at**: Date of review.

### Loyalty Points
- **loyalty_id (PK)**: Unique loyalty record identifier.
- **user_id (FK)**: User receiving points.
- **points**: Number of points awarded.
- **reason**: Reason for points (e.g., "Order", "Promotion").
- **created_at**: Date points were awarded.

## Service Configuration and Access

All configuration is managed via a single `.env` file containing parameters for all services, including credentials, ports, and data generation settings.

### Access Details

#### PostgreSQL
- **URL**: `jdbc:postgresql://localhost:5432/postgres_db?currentSchema=source`
- **Username**: `db_user`
- **Password**: `qwerty`

#### MySQL
- **URL**: `jdbc:mysql://localhost:3306/mysql_db`
- **Username**: `db_user`
- **Password**: `qwerty`

#### Airflow Web UI
- **URL**: `http://localhost:8080`
- **Username**: `admin`
- **Password**: `admin`

#### Spark Master
- **URL**: `http://localhost:8081`

#### Kafka
- **Bootstrap Servers**: `localhost:9092`
- **Topic**: `users-data`

## Data Generation Parameters

**PostgreSQL Data Generator (default settings):**
- Users: 500
- Products: 800
- Orders: 3000
- Order Details: 1 to 10 items per order
- Product Categories: 20
- Product Reviews: 2000
- Loyalty Points: 3000

**Kafka Data Generator (default settings):**
- Event Generation Interval: 5 seconds
- Kafka Topic: `users-data`
- Event Format: JSON with fields such as `first_name`, `last_name`, `email`, `phone`, `registration_date`, and `loyalty_status`.

## Data Replication and Streaming

### Replication Pipeline

Airflow orchestrates data replication from PostgreSQL to MySQL. The replication DAG performs the following tasks:
1. Extract data from PostgreSQL.
2. Transform the data using Spark.
3. Load the transformed data into MySQL.

- **DAG Path**: `code/airflow/dags/replicate_postgres_to_mysql.py`

### Streaming Pipeline

Airflow also manages streaming data from Kafka into PostgreSQL. The streaming DAG executes the following:
1. Retrieve data from the Kafka topic.
2. Process the data using Spark.
3. Save the processed data to PostgreSQL.

- **DAG Path**: `code/airflow/dags/kafka_to_postgres_streaming.py`

## Analytical Data Marts

### User Activity Mart (`mart_user_activity`)

**Description:**  
Provides an analysis of user behavior by summarizing order counts and total spend, segmented by order status.

| Field        | Description                   |
|--------------|-------------------------------|
| user_id      | User identifier               |
| first_name   | User's first name             |
| last_name    | User's last name              |
| status       | Order status                  |
| order_count  | Number of orders              |
| total_spent  | Total amount spent            |

### Product Rating Mart (`mart_product_rating`)

**Description:**  
Analyzes product ratings to understand product popularity and customer satisfaction.

| Field      | Description            |
|------------|------------------------|
| product_id | Product identifier     |
| name       | Product name           |
| rating     | Average product rating |

### Loyalty Points Mart (`mart_user_loyalty_points`)

**Description:**  
Analyzes user loyalty based on the accumulation of bonus points.

| Field                | Description                      |
|----------------------|----------------------------------|
| user_id              | User identifier                  |
| first_name           | User's first name                |
| last_name            | User's last name                 |
| loyalty_status       | Loyalty tier                     |
| total_loyalty_points | Total bonus points accumulated   |

### Average Check Mart (`mart_average_check`)

**Description:**  
Provides insights into average order values segmented by order status and user loyalty.

| Field           | Description                                  |
|-----------------|----------------------------------------------|
| status          | Order status                                 |
| loyalty_status  | User's loyalty tier                          |
| average_check   | Average order value for the segment          |

**Data Mart Creation Process:**
1. Load raw data from PostgreSQL and MySQL.
2. Perform necessary transformations (joins, aggregations, groupings).
3. Save the resulting mart back to the target database.

## Deployment

To deploy the project, run the following command:

```bash
docker compose up --build -d

After deployment, simply unpause the DAGs in the Airflow UI to start the replication and streaming pipelines.

DE2024_PY_CourseWork/
├── .env                # Environment variables for all services
├── docker-compose.yml  # Docker Compose configuration
├── setup/              # Container infrastructure configuration
│   ├── airflow/        # Airflow configuration
│   │   ├── init/       
│   │   ├── scheduler/  
│   │   └── webserver/  
│   ├── datagen/        # Data generator configurations
│   │   ├── pg_datagen/
│   │   └── kafka_datagen/
│   ├── db/             # Database configurations
│   │   ├── mysql/     
│   │   └── postgresql/
│   ├── messaging/      # Zookeeper & Kafka configurations
│   │   ├── kafka/
│   │   ├── kafka_init/
│   │   └── zookeeper/
│   └── spark/          # Spark configurations
│       ├── spark-master/
│       └── spark-worker/
├── code/               # Source code
│   ├── airflow/        # Airflow DAGs and scripts
│   │   ├── dags/       
│   │   └── scripts/    
│   │       ├── helpers/        
│   │       └── pyspark_scripts/ 
│   ├── datagen/        # Data generator scripts
│   │   ├── datagen_postgres/ 
│   │   └── kafka_datagen/    
│   └── scripts/        # Additional scripts
├── postgresdb/         # PostgreSQL models and schemas
│   ├── models.py
│   ├── schemas/
│   │   ├── loyalty_schema.py
│   │   ├── review_schema.py
│   │   ├── user_schema.py
│   │   ├── category_schema.py
│   │   ├── product_schema.py
│   │   ├── order_schema.py
│   │   └── order_detail_schema.py
│   └── db_config.py
└── README.md           # This documentation file
