from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app import crud
from app.schemas.tariff import TariffCreate

def get_auth_headers(client: TestClient) -> dict:
    response = client.post(
        "/api/auth/login",
        data={"username": "admin", "password": "admin"},
    )
    tokens = response.json()
    access_token = tokens["access_token"]
    return {"Authorization": f"Bearer {access_token}"}


def test_create_and_read_tariff(client: TestClient):
    headers = get_auth_headers(client)
    data = {
        "start_date": "2023-01-01",
        "end_date": "2023-12-31",
        "purchase_low_eur_kwh": 0.30,
        "purchase_high_eur_kwh": 0.40,
        "sale_eur_kwh": 0.10,
        "vat": 0.21,
    }
    response = client.post(
        "/api/tariffs/",
        headers=headers,
        json=data,
    )
    assert response.status_code == 201
    content = response.json()
    assert content["start_date"] == data["start_date"]
    assert "id" in content
    tariff_id = content["id"]

    response = client.get(f"/api/tariffs/{tariff_id}", headers=headers)
    assert response.status_code == 200
    content = response.json()
    assert content["start_date"] == data["start_date"]


def test_read_tariffs(client: TestClient):
    headers = get_auth_headers(client)
    # Create a tariff first
    data = {
        "start_date": "2023-01-01",
        "end_date": "2023-12-31",
        "purchase_low_eur_kwh": 0.30,
        "purchase_high_eur_kwh": 0.40,
        "sale_eur_kwh": 0.10,
        "vat": 0.21,
    }
    client.post("/api/tariffs/", headers=headers, json=data)

    response = client.get("/api/tariffs/", headers=headers)
    assert response.status_code == 200
    content = response.json()
    assert len(content) >= 1


def test_update_tariff(client: TestClient):
    headers = get_auth_headers(client)
    # Create a tariff to update
    data = {
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "purchase_low_eur_kwh": 0.35,
        "purchase_high_eur_kwh": 0.45,
        "sale_eur_kwh": 0.15,
        "vat": 0.21,
    }
    response = client.post("/api/tariffs/", headers=headers, json=data)
    tariff_id = response.json()["id"]

    update_data = {"vat": 0.25}
    response = client.put(
        f"/api/tariffs/{tariff_id}",
        headers=headers,
        json=update_data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["vat"] == 0.25


def test_delete_tariff(client: TestClient):
    headers = get_auth_headers(client)
    # Create a tariff to delete
    data = {
        "start_date": "2025-01-01",
        "end_date": "2025-12-31",
        "purchase_low_eur_kwh": 0.38,
        "purchase_high_eur_kwh": 0.48,
        "sale_eur_kwh": 0.18,
        "vat": 0.21,
    }
    response = client.post("/api/tariffs/", headers=headers, json=data)
    tariff_id = response.json()["id"]

    response = client.delete(
        f"/api/tariffs/{tariff_id}",
        headers=headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == tariff_id

    # Verify it's gone
    response = client.get(f"/api/tariffs/{tariff_id}", headers=headers)
    assert response.status_code == 404
