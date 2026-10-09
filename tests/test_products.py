def test_product_data():
    product = {
        "id": 1,
        "name": "Laptop",
        "price": 50000,
        "stock": 10
    }

    assert product["name"] == "Laptop"
    assert product["price"] > 0
    assert product["stock"] >= 0
