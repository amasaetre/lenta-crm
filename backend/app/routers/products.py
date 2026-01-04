from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from app.database import get_session
from app.models import Product, OrderItem

router = APIRouter()


@router.get("/products", response_model=list[Product])
def get_products(session: Session = Depends(get_session)):
    """Получить справочник товаров"""
    statement = select(Product)
    products = session.exec(statement).all()
    return products


@router.get("/products/popular")
def get_popular_products(session: Session = Depends(get_session), limit: int = 10):
    items_statement = select(OrderItem)
    all_items = session.exec(items_statement).all()
    
    product_stats = {}
    
    for item in all_items:
        product_id = item.product_id
        if product_id not in product_stats:
            product_stats[product_id] = {
                'total_quantity': 0,
                'order_count': 0,
                'orders': set()
            }
        
        product_stats[product_id]['total_quantity'] += item.quantity
        product_stats[product_id]['orders'].add(item.order_id)
    
    for product_id, stats in product_stats.items():
        stats['order_count'] = len(stats['orders'])
        del stats['orders']
    
    result = []
    for product_id, stats in product_stats.items():
        product = session.get(Product, product_id)
        if product:
            result.append({
                'product_id': product.id,
                'product_name': product.name,
                'total_quantity': stats['total_quantity'],
                'order_count': stats['order_count']
            })
    
    result.sort(key=lambda x: x['total_quantity'], reverse=True)
    
    return result[:limit]

