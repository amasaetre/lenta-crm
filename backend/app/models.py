from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime


class Product(SQLModel, table=True):
    """Справочник товаров"""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    price: float


class OrderItem(SQLModel, table=True):
    """Позиции заказа"""
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id")
    product_id: int = Field(foreign_key="product.id")
    quantity: int
    price: float


class Order(SQLModel, table=True):
    """Заказы"""
    id: Optional[int] = Field(default=None, primary_key=True)
    customer_name: str
    created_at: datetime = Field(default_factory=datetime.now)
    status: str = Field(default="новый")


class OrderItemCreate(SQLModel):
    """Схема для создания позиции заказа"""
    product_id: int
    quantity: int


class OrderCreate(SQLModel):
    """Схема для создания заказа"""
    customer_name: str
    items: List[OrderItemCreate]


class OrderItemResponse(SQLModel):
    """Схема позиции заказа для ответа"""
    id: int
    product_id: int
    product_name: str
    quantity: int
    price: float
    total: float


class OrderResponse(SQLModel):
    """Схема заказа для ответа"""
    id: int
    customer_name: str
    created_at: datetime
    status: str
    items: List[OrderItemResponse]
    total_amount: float


class OrderStatusUpdate(SQLModel):
    """Схема для обновления статуса заказа"""
    status: str

