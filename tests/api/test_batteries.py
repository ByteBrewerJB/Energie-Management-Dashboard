from fastapi.testclient import TestClient
from tests.api.test_tariffs import get_auth_headers # Re-using the helper

def test_create_and_read_battery(client: TestClient):
    headers = get_auth_headers(client)
    data = {
        "name": "Test Battery",
        "brand": "JouleBrand",
        "purchase_cost_eur": 5000,
        "capacity_kwh": 10,
    }
    response = client.post(
        "/api/batteries/",
        headers=headers,
        json=data,
    )
    assert response.status_code == 201
    content = response.json()
    assert content["name"] == data["name"]
    assert content["brand"] == data["brand"]
    assert "id" in content
    battery_id = content["id"]

    response = client.get(f"/api/batteries/{battery_id}", headers=headers)
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == data["name"]
