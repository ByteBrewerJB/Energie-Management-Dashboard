from fastapi.testclient import TestClient
from tests.api.test_tariffs import get_auth_headers # Re-using the helper

def test_create_and_read_car(client: TestClient):
    headers = get_auth_headers(client)
    data = {
        "name": "My Test Car",
        "reimbursement_rate_eur_per_kwh": 0.25,
    }
    response = client.post(
        "/api/cars/",
        headers=headers,
        json=data,
    )
    assert response.status_code == 201
    content = response.json()
    assert content["name"] == data["name"]
    assert "id" in content
    car_id = content["id"]

    response = client.get(f"/api/cars/{car_id}", headers=headers)
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == data["name"]


def test_update_car(client: TestClient):
    headers = get_auth_headers(client)
    data = {"name": "Another Car", "reimbursement_rate_eur_per_kwh": 0.30}
    response = client.post("/api/cars/", headers=headers, json=data)
    car_id = response.json()["id"]

    update_data = {"name": "My Updated Car Name"}
    response = client.put(
        f"/api/cars/{car_id}",
        headers=headers,
        json=update_data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == update_data["name"]


def test_delete_car(client: TestClient):
    headers = get_auth_headers(client)
    data = {"name": "A Car to Delete", "reimbursement_rate_eur_per_kwh": 0.10}
    response = client.post("/api/cars/", headers=headers, json=data)
    car_id = response.json()["id"]

    response = client.delete(
        f"/api/cars/{car_id}",
        headers=headers,
    )
    assert response.status_code == 200

    # Verify it's gone
    response = client.get(f"/api/cars/{car_id}", headers=headers)
    assert response.status_code == 404
