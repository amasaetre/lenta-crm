from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database import init_db
from app.routers import orders, products


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Информационная система учета интернет-заказов",
    description="Система учета интернет-заказов торговой сети",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(orders.router, prefix="/api", tags=["orders"])
app.include_router(products.router, prefix="/api", tags=["products"])


@app.get("/")
async def root():
    return {"message": "API для системы учета интернет-заказов"}

