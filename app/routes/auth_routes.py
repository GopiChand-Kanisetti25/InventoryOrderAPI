from fastapi import APIRouter
from database import connection
from app.security import hash_password, verify_password

router = APIRouter()


@router.post("/register")
def register_user(username: str, password: str):
    cursor = connection.cursor()

    hashed_password = hash_password(password)

    cursor.execute("""
        INSERT INTO users (username, password)
        VALUES (%s, %s)
        RETURNING id
    """, (username, hashed_password))

    user_id = cursor.fetchone()[0]

    connection.commit()
    cursor.close()

    return {
        "message": "User registered successfully",
        "user_id": user_id
    }
@router.post("/login")
def login_user(username: str, password: str):
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, username, password
        FROM users
        WHERE username = %s
    """, (username,))

    user = cursor.fetchone()

    cursor.close()

    if user is None:
        return {
            "message": "Invalid username or password"
        }

    if not verify_password(password, user[2]):
        return {
            "message": "Invalid username or password"
        }

    return {
        "message": "Login successful",
        "user_id": user[0],
        "username": user[1]
    }