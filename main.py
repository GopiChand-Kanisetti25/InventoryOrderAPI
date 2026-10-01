from fastapi import FastAPI
from app.routes.category_routes import router as category_router
from app.routes.product_routes import router as product_router
from app.routes.order_routes import router as order_router
from app.routes.auth_routes import router as auth_router

app = FastAPI()

app.include_router(category_router)
app.include_router(product_router)
app.include_router(order_router)
app.include_router(auth_router)


@app.get("/")
def home():
    return {
        "message": "Inventory & Order Management API is running"
    }