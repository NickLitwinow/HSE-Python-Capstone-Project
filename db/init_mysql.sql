-- Принимаем, что база "mydb" уже существует (создана при старте).
USE mydb;

CREATE TABLE IF NOT EXISTS users_replica (
    user_id INT PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100),
    phone VARCHAR(20),
    registration_date DATETIME,
    loyalty_status VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS products_replica (
    product_id INT PRIMARY KEY,
    name VARCHAR(100),
    description TEXT,
    category_id INT,
    price DECIMAL(10, 2),
    stock_quantity INT,
    creation_date DATETIME
);

CREATE TABLE IF NOT EXISTS productcategories_replica (
    category_id INT PRIMARY KEY,
    name VARCHAR(100),
    parent_category_id INT
);

CREATE TABLE IF NOT EXISTS orders_replica (
    order_id INT PRIMARY KEY,
    user_id INT,
    order_date DATETIME,
    total_amount DECIMAL(10, 2),
    status VARCHAR(50),
    delivery_date DATETIME
);

CREATE TABLE IF NOT EXISTS orderdetails_replica (
    order_detail_id INT PRIMARY KEY,
    order_id INT,
    product_id INT,
    quantity INT,
    price_per_unit DECIMAL(10, 2),
    total_price DECIMAL(10, 2)
);