from fastapi import APIRouter
from database import connection

router = APIRouter()


@router.get("/categories")
def get_categories():
    cursor = connection.cursor()

    cursor.execute(
        "SELECT id, name, description FROM categories"
    )

    categories = cursor.fetchall()

    cursor.close()

    return categories