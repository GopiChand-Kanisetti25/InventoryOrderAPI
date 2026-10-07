from fastapi import APIRouter
from database import connection
from redis_client import redis_client
import json

router = APIRouter()


# GET ALL PRODUCTS
@router.get("/products")
def get_products():

    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, name, description, price, stock, category_id
        FROM products
    """)

    products = cursor.fetchall()

    cursor.close()

    return products


# CREATE PRODUCT
@router.post("/products")
def create_product(
    name: str,
    description: str,
    price: float,
    stock: int,
    category_id: int
):

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO products
        (name, description, price, stock, category_id)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
    """, (
        name,
        description,
        price,
        stock,
        category_id
    ))

    product_id = cursor.fetchone()[0]

    connection.commit()
    cursor.close()

    return {
        "message": "Product created successfully",
        "product_id": product_id
    }


# GET PRODUCT BY ID
@router.get("/products/id/{product_id}")
def get_product(product_id: int):

    # Check Redis cache first
    cached_product = redis_client.get(f"product:{product_id}")

    if cached_product:
        return json.loads(cached_product)

    # If not in Redis, get product from PostgreSQL
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, name, description, price, stock, category_id
        FROM products
        WHERE id = %s
    """, (product_id,))

    product = cursor.fetchone()

    cursor.close()

    if product is None:
        return {
            "message": "Product not found"
        }

    product_data = {
        "id": product[0],
        "name": product[1],
        "description": product[2],
        "price": float(product[3]),
        "stock": product[4],
        "category_id": product[5]
    }

    # Store product in Redis for 5 minutes
    redis_client.setex(
        f"product:{product_id}",
        300,
        json.dumps(product_data)
    )

    return product_data


# UPDATE PRODUCT
@router.put("/products/{product_id}")
def update_product(
    product_id: int,
    name: str,
    description: str,
    price: float,
    stock: int,
    category_id: int
):

    cursor = connection.cursor()

    cursor.execute("""
        UPDATE products
        SET name = %s,
            description = %s,
            price = %s,
            stock = %s,
            category_id = %s
        WHERE id = %s
    """, (
        name,
        description,
        price,
        stock,
        category_id,
        product_id
    ))

    connection.commit()
    cursor.close()

    # Remove old cached product
    redis_client.delete(f"product:{product_id}")

    return {
        "message": "Product updated successfully"
    }


# SEARCH PRODUCTS
@router.get("/products/search")
def search_products(name: str):

    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, name, description, price, stock, category_id
        FROM products
        WHERE name ILIKE %s
    """, (f"%{name}%",))

    products = cursor.fetchall()

    cursor.close()

    return products


# DELETE PRODUCT
@router.delete("/products/{product_id}")
def delete_product(product_id: int):

    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM products WHERE id = %s",
        (product_id,)
    )

    connection.commit()
    cursor.close()

    # Remove cached product
    redis_client.delete(f"product:{product_id}")

    return {
        "message": "Product deleted successfully"
    }


# UPDATE STOCK
@router.put("/products/{product_id}/stock")
def update_stock(
    product_id: int,
    quantity: int
):

    cursor = connection.cursor()

    cursor.execute("""
        UPDATE products
        SET stock = stock + %s
        WHERE id = %s
    """, (
        quantity,
        product_id
    ))

    connection.commit()
    cursor.close()

    # Remove old cached product
    redis_client.delete(f"product:{product_id}")

    return {
        "message": "Stock updated successfully"
    }
