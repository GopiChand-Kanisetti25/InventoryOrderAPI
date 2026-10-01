from fastapi import APIRouter
from database import connection

router = APIRouter()


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
    """, (name, description, price, stock, category_id))

    product_id = cursor.fetchone()[0]

    connection.commit()
    cursor.close()

    return {
        "message": "Product created successfully",
        "product_id": product_id
    }
@router.get("/products/id/{product_id}")
def get_product(product_id: int):
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, name, description, price, stock, category_id
        FROM products
        WHERE id = %s
    """, (product_id,))

    product = cursor.fetchone()

    cursor.close()

    if product is None:
        return {"message": "Product not found"}

    return product
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

    return {
        "message": "Product updated successfully"
    }
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
@router.delete("/products/{product_id}")
def delete_product(product_id: int):
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM products WHERE id = %s",
        (product_id,)
    )

    connection.commit()
    cursor.close()

    return {
        "message": "Product deleted successfully"
    }
@router.put("/products/{product_id}/stock")
def update_stock(product_id: int, quantity: int):
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE products
        SET stock = stock + %s
        WHERE id = %s
    """, (quantity, product_id))

    connection.commit()
    cursor.close()

    return {
        "message": "Stock updated successfully"
    }
