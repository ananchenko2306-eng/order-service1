import requests
from fastapi.testclient import TestClient
from main import app  # Імпортуємо app з файлу main.py

# Створюємо клієнт для тестування
client = TestClient(app)

def test_create_order_success(requests_mock):
    """
    Тестує успішне створення замовлення, коли всі товари доступні.
    """
    # Arrange (Підготовка)
    requests_mock.get(
        "http://localhost:8080/products/1",
        json={"id": 1, "name": "Laptop", "price": 1200.50}
    )
    requests_mock.get(
        "http://localhost:8080/products/2",
        json={"id": 2, "name": "Smartphone", "price": 800.00}
    )

    order_payload = {
        "items": [
            {"product_id": 1, "quantity": 1},
            {"product_id": 2, "quantity": 2}
        ]
    }

    # Act (Дія)
    response = client.post("/orders", json=order_payload)

    # Assert (Перевірка)
    assert response.status_code == 201
    response_data = response.json()

    assert response_data["items"][0]["product_id"] == 1
    assert response_data["items"][1]["product_id"] == 2

    # 1200.50 * 1 + 800.00 * 2 = 2800.50
    assert response_data["total_amount"] == 2800.50

def test_create_order_product_not_found(requests_mock):
    """
    Тестує випадок, коли один із товарів у замовленні не знайдено.
    """
    # Arrange
    requests_mock.get("http://localhost:8080/products/99", status_code=404)

    order_payload = {
        "items": [
            {"product_id": 99, "quantity": 1}
        ]
    }

    # Act
    response = client.post("/orders", json=order_payload)

    # Assert
    assert response.status_code == 400
    assert "Product with id 99 not found" in response.json()["detail"]

def test_create_order_product_service_unavailable(requests_mock):
    """
    Тестує випадок, коли сервіс продуктів недоступний.
    """
    # Arrange
    requests_mock.get(
        "http://localhost:8080/products/1",
        exc=requests.exceptions.ConnectionError
    )

    order_payload = {
        "items": [
            {"product_id": 1, "quantity": 1}
        ]
    }

    # Act
    response = client.post("/orders", json=order_payload)

    # Assert
    assert response.status_code == 503
    assert "Product service is unavailable" in response.json()["detail"]

