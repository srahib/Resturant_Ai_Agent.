from sqlalchemy import Column, Integer, String, Float, Boolean, Text
from app.database import Base


class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    category = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    available = Column(Boolean, default=True)


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(30), unique=True, nullable=False)
    address = Column(Text, nullable=True)


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)

    customer_id = Column(Integer, nullable=False)

    items = Column(Text, nullable=False)

    subtotal = Column(Float, nullable=False)
    delivery_charges = Column(Float, default=0)
    total = Column(Float, nullable=False)

    order_type = Column(
        String(30),
        default="delivery"
    )

    payment_method = Column(
        String(50),
        nullable=True
    )

    status = Column(
        String(50),
        default="new"
    )

    delivery_address = Column(
        Text,
        nullable=True
    )