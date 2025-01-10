from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Numeric, CheckConstraint, Text, Float
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

# Инициализация базового класса для декларативного определения моделей
Base = declarative_base()

# ================================
# Модель пользователей
# ================================

class User(Base):
    __tablename__ = 'users'  # Название таблицы в базе данных

    user_id = Column(Integer, primary_key=True)  # Первичный ключ, уникальный идентификатор пользователя
    first_name = Column(String(50), nullable=False)  # Имя пользователя, обязательное поле
    last_name = Column(String(50), nullable=False)  # Фамилия пользователя, обязательное поле
    email = Column(String(100), unique=True, nullable=False)  # Электронная почта, уникальное и обязательное поле
    phone = Column(String(20))  # Номер телефона, необязательное поле
    registration_date = Column(DateTime, default=datetime.now)  # Дата регистрации, по умолчанию текущая дата и время
    loyalty_status = Column(String(20), CheckConstraint("loyalty_status IN ('Gold', 'Silver', 'Bronze')"), nullable=False)  # Статус лояльности, обязательное поле с ограничением значений

    # Связи с другими таблицами
    orders = relationship("Order", back_populates="user")  # Связь с заказами пользователя
    reviews = relationship("Review", back_populates="user", cascade="all, delete-orphan")  # Связь с отзывами пользователя с каскадным удалением
    loyalty_points = relationship("LoyaltyPoint", back_populates="user", cascade="all, delete-orphan")  # Связь с бонусными баллами пользователя с каскадным удалением

# ================================
# Модель категорий товаров
# ================================

class ProductCategory(Base):
    __tablename__ = 'productcategories'  # Название таблицы в базе данных

    category_id = Column(Integer, primary_key=True)  # Первичный ключ, уникальный идентификатор категории
    name = Column(String(100), nullable=False)  # Название категории, обязательное поле
    parent_category_id = Column(Integer, ForeignKey('productcategories.category_id'))  # Внешний ключ на родительскую категорию, если есть

    # Связи с другими таблицами
    subcategories = relationship("ProductCategory", backref="parent", remote_side=[category_id])  # Связь с подкатегориями (самоотношение)
    products = relationship("Product", back_populates="category")  # Связь с продуктами, относящимися к этой категории

# ================================
# Модель товаров
# ================================

class Product(Base):
    __tablename__ = 'products'  # Название таблицы в базе данных

    product_id = Column(Integer, primary_key=True)  # Первичный ключ, уникальный идентификатор продукта
    name = Column(String(100), nullable=False)  # Название продукта, обязательное поле
    description = Column(Text)  # Описание продукта, необязательное поле
    category_id = Column(Integer, ForeignKey('productcategories.category_id'))  # Внешний ключ на категорию продукта
    price = Column(Numeric(10, 2), nullable=False)  # Цена продукта, обязательное поле с точностью до двух знаков после запятой
    stock_quantity = Column(Integer, default=0)  # Количество товара на складе, по умолчанию 0
    creation_date = Column(DateTime, default=datetime.now)  # Дата создания записи о продукте, по умолчанию текущая дата и время

    # Связи с другими таблицами
    category = relationship("ProductCategory", back_populates="products")  # Связь с категорией продукта
    order_details = relationship("OrderDetail", back_populates="product")  # Связь с деталями заказов, содержащими этот продукт
    reviews = relationship("Review", back_populates="product", cascade="all, delete-orphan")  # Связь с отзывами о продукте с каскадным удалением

# ================================
# Модель заказов
# ================================

class Order(Base):
    __tablename__ = "orders"  # Название таблицы в базе данных

    order_id = Column(Integer, primary_key=True, index=True)  # Первичный ключ, уникальный идентификатор заказа с индексом для ускорения поиска
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)  # Внешний ключ на пользователя, совершившего заказ, обязательное поле
    order_date = Column(DateTime, nullable=False)  # Дата и время заказа, обязательное поле
    total_amount = Column(Float, nullable=True)  # Общая сумма заказа, необязательное поле
    status = Column(String, nullable=False)  # Статус заказа, обязательное поле
    delivery_date = Column(DateTime, nullable=True)  # Дата доставки заказа, необязательное поле

    # Ограничения таблицы
    __table_args__ = (
        CheckConstraint(
            "status IN ('Pending', 'Completed', 'Canceled', 'Processing', 'Shipped', 'Delivered', 'Returned', 'Failed')",
            name="orders_status_check"  # Имя ограничения
        ),
    )

    # Связи с другими таблицами
    user = relationship("User", back_populates="orders")  # Связь с пользователем, совершившим заказ
    order_details = relationship("OrderDetail", back_populates="order")  # Связь с деталями заказа

# ================================
# Модель деталей заказа
# ================================

class OrderDetail(Base):
    __tablename__ = "orderdetails"  # Название таблицы в базе данных

    order_detail_id = Column(Integer, primary_key=True, index=True)  # Первичный ключ, уникальный идентификатор детали заказа с индексом
    order_id = Column(Integer, ForeignKey("orders.order_id"), nullable=False)  # Внешний ключ на заказ, к которому относится деталь, обязательное поле
    product_id = Column(Integer, ForeignKey("products.product_id"), nullable=False)  # Внешний ключ на продукт, включённый в деталь заказа, обязательное поле
    quantity = Column(Integer, nullable=False)  # Количество единиц продукта в заказе, обязательное поле
    price_per_unit = Column(Float, nullable=False)  # Цена за единицу продукта, обязательное поле
    total_price = Column(Float, nullable=False)  # Общая цена за указанное количество продукта, обязательное поле

    # Связи с другими таблицами
    order = relationship("Order", back_populates="order_details")  # Связь с заказом
    product = relationship("Product")  # Связь с продуктом

# ================================
# Модель отзыва о продукте
# ================================

class Review(Base):
    __tablename__ = "reviews"  # Название таблицы в базе данных

    review_id = Column(Integer, primary_key=True, index=True)  # Первичный ключ, уникальный идентификатор отзыва с индексом
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)  # Внешний ключ на пользователя, оставившего отзыв, с каскадным удалением
    product_id = Column(Integer, ForeignKey("products.product_id", ondelete="CASCADE"), nullable=False)  # Внешний ключ на продукт, к которому относится отзыв, с каскадным удалением
    rating = Column(Integer, nullable=False)  # Рейтинг продукта, обязательное поле (обычно от 1 до 5)
    review_text = Column(Text, nullable=True)  # Текст отзыва, необязательное поле
    created_at = Column(DateTime, default=datetime.utcnow)  # Дата и время создания отзыва, по умолчанию текущее время

    # Связи с другими таблицами
    user = relationship("User", back_populates="reviews")  # Связь с пользователем, оставившим отзыв
    product = relationship("Product", back_populates="reviews")  # Связь с продуктом, к которому относится отзыв

# ================================
# Модель бонусных баллов
# ================================

class LoyaltyPoint(Base):
    __tablename__ = "loyaltypoints"  # Название таблицы в базе данных

    loyalty_id = Column(Integer, primary_key=True, index=True)  # Первичный ключ, уникальный идентификатор бонусного балла с индексом
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)  # Внешний ключ на пользователя, получившего бонусные баллы, с каскадным удалением
    points = Column(Integer, nullable=False)  # Количество бонусных баллов, обязательное поле
    reason = Column(String(255), nullable=False)  # Причина начисления баллов, обязательное поле
    created_at = Column(DateTime, default=datetime.utcnow)  # Дата и время начисления баллов, по умолчанию текущее время

    # Связи с другими таблицами
    user = relationship("User", back_populates="loyalty_points")  # Связь с пользователем, получившим бонусные баллы