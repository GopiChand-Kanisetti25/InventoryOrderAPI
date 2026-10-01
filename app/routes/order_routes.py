from fastapi import APIRouter
from database import connection

router = APIRouter()


@router.get("/orders")
def get_orders():
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, customer_name, total_amount, status, created_at
        FROM orders
        ORDER BY id DESC
    """)

    orders = cursor.fetchall()

    cursor.close()

    return orders


@router.post("/orders")
def create_order(
    customer_name: str,
    total_amount: float
):
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO orders (customer_name, total_amount)
        VALUES (%s, %s)
        RETURNING id
    """, (customer_name, total_amount))

    order_id = cursor.fetchone()[0]

    connection.commit()
    cursor.close()

    return {
        "message": "Order created successfully",
        "order_id": order_id
    }
@router.get("/orders/{order_id}")
def get_order(order_id: int):
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, customer_name, total_amount, status, created_at
        FROM orders
        WHERE id = %s
    """, (order_id,))

    order = cursor.fetchone()

    cursor.close()

    if order is None:
        return {"message": "Order not found"}

    return order
@router.put("/orders/{order_id}/status")
def update_order_status(
    order_id: int,
    status: str
):
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE orders
        SET status = %s
        WHERE id = %s
    """, (status, order_id))

    connection.commit()
    cursor.close()

    return {
        "message": "Order status updated successfully"
    }
@router.post("/orders/{order_id}/items")
def add_order_item(
    order_id: int,
    product_id: int,
    quantity: int
):
    cursor = connection.cursor()

    cursor.execute("""
        SELECT price, stock
        FROM products
        WHERE id = %s
    """, (product_id,))

    product = cursor.fetchone()

    if product is None:
        cursor.close()
        return {"message": "Product not found"}

    price = product[0]
    stock = product[1]

    if stock < quantity:
        cursor.close()
        return {"message": "Insufficient stock"}

    cursor.execute("""
        INSERT INTO order_items
        (order_id, product_id, quantity, price)
        VALUES (%s, %s, %s, %s)
        RETURNING id
    """, (order_id, product_id, quantity, price))

    item_id = cursor.fetchone()[0]

    cursor.execute("""
        UPDATE products
        SET stock = stock - %s
        WHERE id = %s
    """, (quantity, product_id))

    cursor.execute("""
    UPDATE orders
    SET total_amount = total_amount + (%s * %s)
    WHERE id = %s
    """, (quantity, price, order_id))

    connection.commit()
    cursor.close()

    return {
        "message": "Order item added successfully",
        "item_id": item_id
    }
@router.get("/orders/{order_id}/items")
def get_order_items(order_id: int):
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            oi.id,
            oi.product_id,
            p.name,
            oi.quantity,
            oi.price
        FROM order_items oi
        JOIN products p
            ON oi.product_id = p.id
        WHERE oi.order_id = %s
    """, (order_id,))

    items = cursor.fetchall()

    cursor.close()

    return items