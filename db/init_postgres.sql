-- Скрипт идемпотентно создаёт нужные таблицы в базе "postgres".
-- При повторном запуске ошибки не произойдут, если таблицы уже есть.

CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100),
    phone VARCHAR(50),
    registration_date TIMESTAMP,
    loyalty_status VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS products (
    product_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    description TEXT,
    category_id INT,
    price DECIMAL(10, 2),
    stock_quantity INT,
    creation_date TIMESTAMP
);

CREATE TABLE IF NOT EXISTS productcategories (
    category_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    parent_category_id INT
);

CREATE TABLE IF NOT EXISTS orders (
    order_id SERIAL PRIMARY KEY,
    user_id INT,
    order_date TIMESTAMP,
    total_amount DECIMAL(10, 2),
    status VARCHAR(50),
    delivery_date TIMESTAMP
);

CREATE TABLE IF NOT EXISTS orderdetails (
    order_detail_id SERIAL PRIMARY KEY,
    order_id INT,
    product_id INT,
    quantity INT,
    price_per_unit DECIMAL(10, 2),
    total_price DECIMAL(10, 2)
);

-- Создаём базу (если нет)
CREATE DATABASE airflowdb;

-- Создаём пользователя airflow (если нет)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT FROM pg_catalog.pg_roles
        WHERE rolname = 'airflow') THEN
        CREATE ROLE airflow LOGIN PASSWORD 'airflow';
    END IF;
END
$$;

-- Выдаём права пользователю airflow на БД airflowdb
GRANT ALL PRIVILEGES ON DATABASE airflowdb TO airflow;

-- Подключаемся к базе airflowdb, чтобы поменять права на схему public
ALTER DATABASE airflowdb OWNER TO airflow;

-- Запускаем plpgsql-блок, чтобы выполнить команды внутри airflowdb:
DO $$
DECLARE
    _dbname text := 'airflowdb';
BEGIN
    -- Передаём ownership схемы public пользователю airflow
    EXECUTE format('ALTER SCHEMA public OWNER TO %I', 'airflow');
    -- Или даём полный доступ
    EXECUTE format('GRANT ALL ON SCHEMA public TO %I', 'airflow');
END
$$;