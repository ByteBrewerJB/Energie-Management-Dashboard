from fastapi.testclient import TestClient
from tests.api.test_tariffs import get_auth_headers # Re-using the helper

def test_create_and_read_solar_panel(client: TestClient):
    headers = get_auth_headers(client)
    data = {
        "name": "Test Solar Panels",
        "purchase_cost_eur": 8000,
        "power_capacity_kwp": 5.5,
    }
    response = client.post(
        "/api/solar_panels/",
        headers=headers,
        json=data,
    )
    assert response.status_code == 201
    content = response.json()
    assert content["name"] == data["name"]
    assert "id" in content
    solar_panel_id = content["id"]

    response = client.get(f"/api/solar_panels/{solar_panel_id}", headers=headers)
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == data["name"]
