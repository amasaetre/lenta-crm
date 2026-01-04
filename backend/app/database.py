from sqlmodel import SQLModel, create_engine, Session, select
from app.models import Product, Order, OrderItem

DATABASE_URL = "sqlite:///./lenta_orders.db"

engine = create_engine(DATABASE_URL, echo=False)


def init_db():
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        statement = select(Product)
        existing_products = session.exec(statement).first()
        if not existing_products:
            products = [
                Product(name="Молоко 3.2% 1л", price=89.90),
                Product(name="Хлеб белый нарезной", price=45.50),
                Product(name="Яйца куриные С0, 10шт", price=95.00),
                Product(name="Масло сливочное 82.5% 180г", price=125.00),
                Product(name="Сахар-песок 1кг", price=78.90),
                Product(name="Макароны 500г", price=52.00),
                Product(name="Рис круглозерный 800г", price=89.00),
                Product(name="Мука пшеничная 1кг", price=65.00),
                Product(name="Соль поваренная 1кг", price=28.50),
                Product(name="Чай черный 100г", price=145.00),
            ]
            for product in products:
                session.add(product)
            session.commit()


def get_session():
    with Session(engine) as session:
        yield session

