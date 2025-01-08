#!/usr/bin/env python3
import psycopg2
import random
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()

def generate_users(cur, conn):
    cur.execute("SELECT COUNT(*) FROM users;")
    count_users = cur.fetchone()[0]
    if count_users == 0:
        print("[data_generation] Generating users...")
        for _ in range(100):
            first_name = fake.first_name()
            last_name = fake.last_name()
            email = fake.email()
            phone = fake.phone_number()
            registration_date = fake.date_time_between(start_date='-1y', end_date='now')
            loyalty_status = random.choice(["Gold", "Silver", "Bronze"])
            cur.execute("""
                INSERT INTO users 
                (first_name, last_name, email, phone, registration_date, loyalty_status)
                VALUES (%s, %s, %s, %s, %s, %s);
            """, (first_name, last_name, email, phone, registration_date, loyalty_status))
        conn.commit()
    else:
        print("[data_generation] 'users' table already has data, skipping...")

def generate_product_categories(cur, conn):
    cur.execute("SELECT COUNT(*) FROM productcategories;")
    if cur.fetchone()[0] == 0:
        print("[data_generation] Generating product categories...")
        categories = [
            ("Electronics", None),
            ("Clothing", None),
            ("Books", None),
            ("Smartphones", 1),
            ("Laptops", 1),
            ("Fiction", 3),
            ("Non-fiction", 3),
        ]
        for (cat_name, parent_id) in categories:
            cur.execute("""
                INSERT INTO productcategories (name, parent_category_id)
                VALUES (%s, %s);
            """, (cat_name, parent_id))
        conn.commit()
    else:
        print("[data_generation] 'productcategories' already has data, skipping...")

def generate_products(cur, conn):
    cur.execute("SELECT COUNT(*) FROM products;")
    if cur.fetchone()[0] == 0:
        print("[data_generation] Generating products...")
        for _ in range(50):
            name = fake.word().capitalize() + " " + fake.word().capitalize()
            description = fake.text(max_nb_chars=100)
            category_id = random.randint(1, 7)
            price = round(random.uniform(10, 2000), 2)
            stock_quantity = random.randint(0, 500)
            creation_date = fake.date_time_between(start_date='-2y', end_date='now')
            cur.execute("""
                INSERT INTO products 
                (name, description, category_id, price, stock_quantity, creation_date)
                VALUES (%s, %s, %s, %s, %s, %s);
            """, (name, description, category_id, price, stock_quantity, creation_date))
        conn.commit()
    else:
        print("[data_generation] 'products' already has data, skipping...")

def generate_orders_and_details(cur, conn):
    cur.execute("SELECT COUNT(*) FROM orders;")
    if cur.fetchone()[0] == 0:
        print("[data_generation] Generating orders and orderdetails...")
        cur.execute("SELECT user_id FROM users;")
        user_ids = [row[0] for row in cur.fetchall()]

        cur.execute("SELECT product_id, price FROM products;")
        products_data = cur.fetchall()

        for _ in range(200):
            user_id = random.choice(user_ids)
            order_date = fake.date_time_between(start_date='-1y', end_date='now')
            status = random.choice(["Pending", "Completed", "Cancelled"])
            delivery_date = (order_date + timedelta(days=random.randint(1, 10))) if status != "Cancelled" else None
            cur.execute("""
                INSERT INTO orders (user_id, order_date, total_amount, status, delivery_date)
                VALUES (%s, %s, %s, %s, %s) RETURNING order_id;
            """, (user_id, order_date, 0, status, delivery_date))
            order_id = cur.fetchone()[0]

            num_order_details = random.randint(1, 5)
            order_total_amount = 0
            for _od in range(num_order_details):
                product_id, product_price = random.choice(products_data)
                quantity = random.randint(1, 5)
                price_per_unit = product_price
                total_price = round(price_per_unit * quantity, 2)
                order_total_amount += total_price

                cur.execute("""
                    INSERT INTO orderdetails 
                    (order_id, product_id, quantity, price_per_unit, total_price)
                    VALUES (%s, %s, %s, %s, %s);
                """, (order_id, product_id, quantity, price_per_unit, total_price))

            cur.execute("""
                UPDATE orders
                SET total_amount = %s
                WHERE order_id = %s;
            """, (order_total_amount, order_id))

        conn.commit()
    else:
        print("[data_generation] 'orders' already has data, skipping...")

def main():
    print("=== Starting data generation for PostgreSQL ===")
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="postgres",
        host="postgres_db",
        port="5432"
    )
    cur = conn.cursor()

    # 1) Users
    generate_users(cur, conn)
    # 2) Product categories
    generate_product_categories(cur, conn)
    # 3) Products
    generate_products(cur, conn)
    # 4) Orders + OrderDetails
    generate_orders_and_details(cur, conn)

    cur.close()
    conn.close()
    print("=== Data generation completed ===")

if __name__ == "__main__":
    main()