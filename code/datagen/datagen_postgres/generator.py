from faker import Faker
import random
from postgresdb.models import User, ProductCategory, Product, Order, OrderDetail, Review, LoyaltyPoint
from postgresdb_schemas.loyalty_schema import LoyaltyPointCreate
from postgresdb_schemas.review_schema import ReviewCreate
from postgresdb_schemas.user_schema import UserCreate
from postgresdb_schemas.category_schema import CategoryCreate
from postgresdb_schemas.product_schema import ProductCreate
from postgresdb_schemas.order_schema import OrderCreate, OrderDetailCreate
from postgresdb.db_config import get_session
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import timedelta
import os


def clean_phone(phone: str) -> str:
    """Очистка телефонного номера от лишних символов и обрезка до 20 символов"""
    import re
    cleaned = re.sub(r"[^\d+]", "", phone)  # Удаление всех символов, кроме цифр и '+'
    return cleaned[:20]  # Обрезка до 20 символов


def generate_data():
    """Функция для очистки базы и генерации большого количества тестовых данных."""
    fake = Faker()  # Инициализация Faker для генерации случайных данных
    session: Session = get_session()  # Получение сессии SQLAlchemy для взаимодействия с базой данных

    # Получение количества данных из переменных окружения или установка значений по умолчанию
    num_users = int(os.getenv('PG_DATAGEN_NUM_USERS', 500))
    num_products = int(os.getenv('PG_DATAGEN_NUM_PRODUCTS', 800))
    num_orders = int(os.getenv('PG_DATAGEN_NUM_ORDERS', 3000))
    num_order_details_min = int(os.getenv('PG_DATAGEN_NUM_ORDER_DETAILS_MIN', 1))
    num_order_details_max = int(os.getenv('PG_DATAGEN_NUM_ORDER_DETAILS_MAX', 10))
    num_reviews = int(os.getenv('PG_DATAGEN_NUM_REVIEWS', 2000))
    num_loyalty_points = int(os.getenv('PG_DATAGEN_NUM_LOYALTY_POINTS', 3000))

    try:
        # ================================
        # Генерация пользователей
        # ================================
        print("Генерация пользователей...")
        generated_emails = set()  # Набор для хранения уникальных email
        user_registration_dates = {}  # Словарь для хранения дат регистрации пользователей

        for _ in range(num_users):
            while True:
                email = fake.email()  # Генерация случайного email
                if email not in generated_emails:
                    generated_emails.add(email)  # Добавление уникального email в набор
                    break

            registration_date = fake.date_time_between(start_date='-1y', end_date='now')  # Случайная дата регистрации

            # Сбор данных пользователя
            user_data = {
                "first_name": fake.first_name(),  # Генерация случайного имени
                "last_name": fake.last_name(),    # Генерация случайной фамилии
                "email": email,
                "phone": clean_phone(fake.phone_number()),  # Генерация и очистка номера телефона
                "registration_date": registration_date,
                "loyalty_status": random.choice(['Gold', 'Silver', 'Bronze']),  # Случайный статус лояльности
            }

            # Создание экземпляра схемы пользователя и модели
            user_schema = UserCreate(**user_data)
            user = User(**user_schema.model_dump())
            session.add(user)  # Добавление пользователя в сессию
            session.flush()    # Применение изменений для получения user_id

            # Сохранение даты регистрации для пользователя
            user_registration_dates[user.user_id] = registration_date

        session.commit()  # Сохранение всех изменений в базе данных

        # ================================
        # Генерация категорий товаров
        # ================================
        print("Генерация категорий товаров...")
        expanded_categories = {
            "Electronics": ["Smartphones", "Laptops", "Tablets", "Audio", "Televisions", "Smart Devices", "Cameras"],
            "Books": ["Fiction", "Non-Fiction", "Children’s Books", "Educational", "Comics & Graphic Novels", "Cookbooks"],
            "Clothing": ["Men's Clothing", "Women's Clothing", "Children's Clothing", "Sportswear", "Accessories"],
            "Home Appliances": ["Kitchen Appliances", "Cleaning Appliances", "Heating & Cooling"],
            "Toys": ["Action Figures", "Educational Toys", "Board Games", "Dolls", "Puzzles"],
        }

        category_ids = {}  # Словарь для хранения ID категорий
        for group, subcategories in expanded_categories.items():
            # Создание группы категорий
            category_data = {"name": group, "parent_category_id": None}
            category_schema = CategoryCreate(**category_data)
            group_category = ProductCategory(**category_schema.model_dump())
            session.add(group_category)
            session.flush()  # Применение изменений для получения category_id

            subcategory_ids = []
            for subcategory in subcategories:
                # Создание подкатегорий
                subcategory_data = {"name": subcategory, "parent_category_id": group_category.category_id}
                subcategory_schema = CategoryCreate(**subcategory_data)
                subcategory_instance = ProductCategory(**subcategory_schema.model_dump())
                session.add(subcategory_instance)
                session.flush()  # Применение изменений для получения category_id
                subcategory_ids.append(subcategory_instance.category_id)

            category_ids[group] = {"group_id": group_category.category_id, "subcategories": subcategory_ids}

        session.commit()  # Сохранение всех изменений в базе данных

        # ================================
        # Генерация товаров
        # ================================
        print("Генерация товаров...")
        for _ in range(num_products):
            group = random.choice(list(expanded_categories.keys()))  # Выбор случайной группы категорий
            subcategory_id = random.choice(category_ids[group]["subcategories"])  # Выбор случайной подкатегории
            product_data = {
                "name": fake.word(),  # Генерация случайного названия товара
                "description": fake.text(max_nb_chars=200),  # Генерация случайного описания
                "category_id": subcategory_id,
                "price": round(random.uniform(10, 1000), 2),  # Случайная цена товара
                "stock_quantity": random.randint(0, 100),       # Случайное количество на складе
            }
            product_schema = ProductCreate(**product_data)
            product = Product(**product_schema.model_dump())
            session.add(product)  # Добавление товара в сессию

        session.commit()  # Сохранение всех изменений в базе данных

        # ================================
        # Получение существующих user_id и product_id
        # ================================
        user_ids = [row[0] for row in session.execute(text("SELECT user_id FROM users")).fetchall()]
        product_ids = [row[0] for row in session.execute(text("SELECT product_id FROM products")).fetchall()]

        # ================================
        # Генерация заказов и деталей заказов
        # ================================
        print("Генерация заказов...")
        order_statuses = [
            "Pending",     # В ожидании
            "Completed",   # Завершен
            "Canceled",    # Отменен
            "Processing",  # В обработке
            "Shipped",     # Отправлен
            "Delivered",   # Доставлен
            "Returned",    # Возвращен
            "Failed",      # Неудачный
        ]

        for _ in range(num_orders):
            user_id = random.choice(user_ids)  # Выбор случайного пользователя
            registration_date = user_registration_dates[user_id]  # Получение даты регистрации пользователя

            # Генерация даты заказа после даты регистрации
            order_date = fake.date_time_between(start_date=registration_date, end_date='now')
            delivery_date = fake.date_time_between(start_date=order_date, end_date=order_date + timedelta(days=30))

            total_amount = 0  # Инициализация общей суммы заказа

            # Генерация деталей заказа
            order_details = []
            for _ in range(random.randint(num_order_details_min, num_order_details_max)):
                product_id = random.choice(product_ids)  # Выбор случайного продукта
                quantity = random.randint(1, 5)         # Случайное количество
                price_per_unit = round(random.uniform(10, 1000), 2)  # Случайная цена за единицу
                total_price = quantity * price_per_unit
                total_amount += total_price

                order_details.append({
                    "product_id": product_id,
                    "quantity": quantity,
                    "price_per_unit": price_per_unit,
                    "total_price": round(total_price, 2),
                })

            # Сбор данных заказа
            order_data = {
                "user_id": user_id,
                "order_date": order_date,
                "status": random.choice(order_statuses),
                "delivery_date": delivery_date,
                "total_amount": round(total_amount, 2)
            }

            # Создание заказа
            order_schema = OrderCreate(**order_data)
            order = Order(**order_schema.model_dump())
            session.add(order)
            session.flush()  # Применение изменений для получения order_id

            # Добавление деталей заказа в базу
            for detail in order_details:
                order_detail_schema = OrderDetailCreate(**detail)
                order_detail = OrderDetail(order_id=order.order_id, **order_detail_schema.model_dump())
                session.add(order_detail)

        session.commit()  # Сохранение всех изменений в базе данных

        # ================================
        # Генерация отзывов
        # ================================
        print("Генерация отзывов...")
        for _ in range(num_reviews):
            user_id = random.choice(user_ids)        # Выбор случайного пользователя
            product_id = random.choice(product_ids)  # Выбор случайного продукта
            review_data = {
                "user_id": user_id,
                "product_id": product_id,
                "rating": random.randint(1, 5),  # Случайный рейтинг от 1 до 5
                "review_text": fake.text(max_nb_chars=200)  # Случайный текст отзыва
            }
            review_schema = ReviewCreate(**review_data)
            review = Review(**review_schema.model_dump())
            session.add(review)  # Добавление отзыва в сессию
        session.commit()  # Сохранение всех изменений в базе данных

        # ================================
        # Генерация бонусных баллов
        # ================================
        print("Генерация бонусных баллов...")
        for _ in range(num_loyalty_points):
            user_id = random.choice(user_ids)  # Выбор случайного пользователя
            loyalty_data = {
                "user_id": user_id,
                "points": random.randint(10, 500),  # Случайное количество баллов
                "reason": random.choice(["Order", "Promotion", "Event Participation"])  # Причина начисления
            }
            loyalty_schema = LoyaltyPointCreate(**loyalty_data)
            loyalty_point = LoyaltyPoint(**loyalty_schema.model_dump())
            session.add(loyalty_point)  # Добавление бонусных баллов в сессию
        session.commit()  # Сохранение всех изменений в базе данных

        print("Данные успешно сгенерированы!")

    except Exception as e:
        print(f"Ошибка генерации данных: {e}")
        session.rollback()  # Откат всех изменений в случае ошибки
    finally:
        session.close()  # Закрытие сессии SQLAlchemy