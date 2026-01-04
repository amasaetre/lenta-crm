from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from app.database import get_session
from app.models import (
    Order, OrderItem, Product,
    OrderCreate, OrderResponse, OrderItemResponse, OrderStatusUpdate
)

router = APIRouter()


@router.get("/orders", response_model=List[dict])
def get_orders(session: Session = Depends(get_session)):
    """Получить список всех заказов"""
    statement = select(Order).order_by(Order.created_at.desc())
    orders = session.exec(statement).all()
    
    result = []
    for order in orders:
        items_statement = select(OrderItem).where(OrderItem.order_id == order.id)
        items = session.exec(items_statement).all()
        
        total = sum(item.price * item.quantity for item in items)
        
        result.append({
            "id": order.id,
            "customer_name": order.customer_name,
            "created_at": order.created_at,
            "status": order.status,
            "total_amount": total
        })
    
    return result


@router.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, session: Session = Depends(get_session)):
    """Получить карточку заказа"""
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    
    items_statement = select(OrderItem).where(OrderItem.order_id == order_id)
    items = session.exec(items_statement).all()
    
    order_items = []
    total_amount = 0
    
    for item in items:
        product = session.get(Product, item.product_id)
        if product:
            item_total = item.price * item.quantity
            total_amount += item_total
            order_items.append(OrderItemResponse(
                id=item.id,
                product_id=item.product_id,
                product_name=product.name,
                quantity=item.quantity,
                price=item.price,
                total=item_total
            ))
    
    return OrderResponse(
        id=order.id,
        customer_name=order.customer_name,
        created_at=order.created_at,
        status=order.status,
        items=order_items,
        total_amount=total_amount
    )


@router.post("/orders", response_model=OrderResponse)
def create_order(order_data: OrderCreate, session: Session = Depends(get_session)):
    order = Order(
        customer_name=order_data.customer_name,
        status="новый"
    )
    session.add(order)
    session.commit()
    session.refresh(order)
    
    total_amount = 0
    order_items = []
    
    for item_data in order_data.items:
        product = session.get(Product, item_data.product_id)
        if not product:
            raise HTTPException(
                status_code=404,
                detail=f"Товар с id {item_data.product_id} не найден"
            )
        
        order_item = OrderItem(
            order_id=order.id,
            product_id=item_data.product_id,
            quantity=item_data.quantity,
            price=product.price
        )
        session.add(order_item)
        
        item_total = product.price * item_data.quantity
        total_amount += item_total
        
        order_items.append(OrderItemResponse(
            id=order_item.id if order_item.id else 0,
            product_id=product.id,
            product_name=product.name,
            quantity=item_data.quantity,
            price=product.price,
            total=item_total
        ))
    
    session.commit()
    
    items_statement = select(OrderItem).where(OrderItem.order_id == order.id)
    items = session.exec(items_statement).all()
    for i, item in enumerate(items):
        order_items[i].id = item.id
    
    return OrderResponse(
        id=order.id,
        customer_name=order.customer_name,
        created_at=order.created_at,
        status=order.status,
        items=order_items,
        total_amount=total_amount
    )


@router.patch("/orders/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: int,
    status_update: OrderStatusUpdate,
    session: Session = Depends(get_session)
):
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    
    valid_statuses = ["новый", "в обработке", "выполнен", "отменен"]
    if status_update.status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Недопустимый статус. Допустимые: {', '.join(valid_statuses)}"
        )
    
    order.status = status_update.status
    session.add(order)
    session.commit()
    session.refresh(order)
    
    return get_order(order_id, session)


@router.get("/orders/stats/summary")
def get_orders_stats(session: Session = Depends(get_session)):
    statement = select(Order)
    orders = session.exec(statement).all()
    
    total_orders = len(orders)
    
    status_counts = {}
    total_amount = 0
    
    for order in orders:
        status = order.status
        status_counts[status] = status_counts.get(status, 0) + 1
        
        items_statement = select(OrderItem).where(OrderItem.order_id == order.id)
        items = session.exec(items_statement).all()
        order_total = sum(item.price * item.quantity for item in items)
        total_amount += order_total
    
    return {
        "total_orders": total_orders,
        "status_counts": status_counts,
        "total_amount": total_amount
    }

