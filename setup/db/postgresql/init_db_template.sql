-- БД, юзер и гранты
CREATE DATABASE ${POSTGRESQL_APP_DB};
CREATE USER ${POSTGRESQL_APP_USER} WITH PASSWORD '${POSTGRESQL_APP_PASSWORD}';
GRANT ALL PRIVILEGES ON DATABASE ${POSTGRESQL_APP_DB} TO ${POSTGRESQL_APP_USER};

-- Подключение к БД
\c ${POSTGRESQL_APP_DB}

-- Создание схемы, изменение дефолтной схемы и гранты
CREATE SCHEMA IF NOT EXISTS ${POSTGRESQL_APP_SCHEMA} AUTHORIZATION ${POSTGRESQL_APP_USER};
SET search_path TO ${POSTGRESQL_APP_SCHEMA};

ALTER DEFAULT PRIVILEGES IN SCHEMA ${POSTGRESQL_APP_SCHEMA} GRANT ALL PRIVILEGES ON TABLES TO ${POSTGRESQL_APP_USER};
ALTER DEFAULT PRIVILEGES IN SCHEMA ${POSTGRESQL_APP_SCHEMA} GRANT USAGE ON SEQUENCES TO ${POSTGRESQL_APP_USER};

-- Создание таблицы users
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    registration_date TIMESTAMP NOT NULL,
    loyalty_status VARCHAR(20) CHECK (loyalty_status IN ('Gold', 'Silver', 'Bronze'))
);

-- Создание таблицы productcategories
CREATE TABLE IF NOT EXISTS productcategories (
    category_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    parent_category_id INT REFERENCES productcategories(category_id) ON DELETE SET NULL
);

-- Создание таблицы products
CREATE TABLE IF NOT EXISTS products (
    product_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    category_id INT REFERENCES productcategories(category_id) ON DELETE CASCADE,
    price NUMERIC(10, 2) NOT NULL CHECK (price >= 0),
    stock_quantity INT NOT NULL CHECK (stock_quantity >= 0),
    creation_date TIMESTAMP DEFAULT NOW()
);

-- Создание таблицы orders
CREATE TABLE IF NOT EXISTS orders (
    order_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
    order_date TIMESTAMP NOT NULL,
    total_amount NUMERIC(10, 2) NOT NULL CHECK (total_amount >= 0),
    status VARCHAR(20) NOT NULL CHECK (status IN ('Pending', 'Completed', 'Canceled', 'Processing', 'Shipped', 'Delivered', 'Returned', 'Failed')),
    delivery_date TIMESTAMP
);

-- Создание таблицы orderdetails
CREATE TABLE IF NOT EXISTS orderdetails (
    order_detail_id SERIAL PRIMARY KEY,
    order_id INT REFERENCES orders(order_id) ON DELETE CASCADE,
    product_id INT REFERENCES products(product_id) ON DELETE CASCADE,
    quantity INT NOT NULL CHECK (quantity > 0),
    price_per_unit NUMERIC(10, 2) NOT NULL CHECK (price_per_unit >= 0),
    total_price NUMERIC(10, 2) NOT NULL CHECK (total_price >= 0)
);

-- Создание таблицы reviews
CREATE TABLE IF NOT EXISTS reviews (
    review_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    product_id INT NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
    rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    review_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создание таблицы loyaltypoints
CREATE TABLE IF NOT EXISTS loyaltypoints (
    loyalty_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    points INT NOT NULL,
    reason VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индексы для ускорения выборок
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_products_category_id ON products(category_id);
CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_orderdetails_order_id ON orderdetails(order_id);
CREATE INDEX IF NOT EXISTS idx_orderdetails_product_id ON orderdetails(product_id);
CREATE INDEX IF NOT EXISTS idx_reviews_user_id ON reviews(user_id);
CREATE INDEX IF NOT EXISTS idx_reviews_product_id ON reviews(product_id);
CREATE INDEX IF NOT EXISTS idx_loyaltypoints_user_id ON loyaltypoints(user_id);
