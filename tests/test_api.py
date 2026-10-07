# tests/test_api.py
from unittest.mock import MagicMock, patch

import requests


# ---------- GET ----------
def test_get_all_items(client):
    response = client.get("/inventory")
    assert response.status_code == 200
    assert len(response.get_json()) == 3


def test_get_one_item(client):
    response = client.get("/inventory/2")
    assert response.status_code == 200
    assert response.get_json()["product_name"] == "Nutella"


def test_get_item_not_found(client):
    response = client.get("/inventory/99")
    assert response.status_code == 404
    assert "error" in response.get_json()


# ---------- POST ----------
def test_add_item(client):
    payload = {"product_name": "Test Cereal", "price": 2.5, "stock": 10}
    response = client.post("/inventory", json=payload)
    assert response.status_code == 201
    body = response.get_json()
    assert body["id"] == 4
    assert body["product_name"] == "Test Cereal"
    assert len(client.get("/inventory").get_json()) == 4


def test_add_item_missing_name(client):
    response = client.post("/inventory", json={"price": 1.0})
    assert response.status_code == 400


# ---------- PATCH ----------
def test_update_item(client):
    response = client.patch("/inventory/1", json={"price": 2.49, "stock": 35})
    assert response.status_code == 200
    body = response.get_json()
    assert body["price"] == 2.49
    assert body["stock"] == 35


def test_update_cannot_change_id(client):
    response = client.patch("/inventory/1", json={"id": 999})
    assert response.get_json()["id"] == 1


def test_update_item_not_found(client):
    response = client.patch("/inventory/99", json={"price": 1.0})
    assert response.status_code == 404


# ---------- DELETE ----------
def test_delete_item(client):
    response = client.delete("/inventory/3")
    assert response.status_code == 200
    assert client.get("/inventory/3").status_code == 404


def test_delete_item_not_found(client):
    response = client.delete("/inventory/99")
    assert response.status_code == 404


# ---------- External API (mocked) ----------
def make_mock_response(json_data):
    mock = MagicMock()
    mock.json.return_value = json_data
    mock.raise_for_status.return_value = None
    return mock


@patch("app.requests.get")
def test_lookup_by_barcode(mock_get, client):
    mock_get.return_value = make_mock_response(
        {
            "status": 1,
            "product": {
                "code": "3017620422003",
                "product_name": "Nutella",
                "brands": "Ferrero",
                "ingredients_text": "Sugar, palm oil, hazelnuts",
            },
        }
    )
    response = client.get("/lookup?barcode=3017620422003")
    assert response.status_code == 200
    assert response.get_json()["product_name"] == "Nutella"


@patch("app.requests.get")
def test_lookup_barcode_not_found(mock_get, client):
    mock_get.return_value = make_mock_response({"status": 0})
    response = client.get("/lookup?barcode=0000000000000")
    assert response.status_code == 404


@patch("app.requests.get")
def test_lookup_by_name(mock_get, client):
    mock_get.return_value = make_mock_response(
        {"products": [{"code": "123", "product_name": "Nutella", "brands": "Ferrero"}]}
    )
    response = client.get("/lookup?name=nutella")
    assert response.status_code == 200
    assert response.get_json()["product_name"] == "Nutella"


@patch("app.requests.get")
def test_lookup_api_down(mock_get, client):
    mock_get.side_effect = requests.exceptions.ConnectionError()
    response = client.get("/lookup?barcode=3017620422003")
    assert response.status_code == 502


def test_lookup_no_params(client):
    response = client.get("/lookup")
    assert response.status_code == 400