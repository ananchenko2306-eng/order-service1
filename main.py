from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import List, Dict
from datetime import date, timedelta

app = FastAPI()

class OrderItem(BaseModel):
    product_id: int
    quantity: int

class Order(BaseModel):
    id: int
    items: List[OrderItem]
    total_amount: float = 0.0

    delivery_date: date
orders: Dict[int, Order] = {}
last_order_id = 0
@app.get("/orders", response_model=List[Order])
def get_all_orders():
    return list(orders.values())

@app.post("/orders", response_model=Order, status_code=status.HTTP_201_CREATED)
def create_order(order_items: List[OrderItem]):
    global last_order_id
    last_order_id += 1

    expected_date = date.today() + timedelta(days=5)

    new_order = Order(
        id=last_order_id,
        items=order_items,
        delivery_date=expected_date
    )

    orders[last_order_id] = new_order
    return new_order

@app.get("/orders/{order_id}", response_model=Order)
def get_order_by_id(order_id: int):
    if order_id not in orders:
        raise HTTPException(status_code=404, detail="Order not found")
    return orders[order_id]

@app.delete("/orders/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(order_id: int):
    if order_id not in orders:
        raise HTTPException(status_code=404, detail="Order not found")
    del orders[order_id]
    return
