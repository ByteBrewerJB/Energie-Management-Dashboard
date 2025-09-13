from fastapi.testclient import TestClient
from tests.api.test_tariffs import get_auth_headers

def test_get_roi_endpoints(client: TestClient):
    headers = get_auth_headers(client)

    # 1. Create a Solar Panel
    panel_data = {"name": "ROI Test Panels", "purchase_cost_eur": 10000, "power_capacity_kwp": 5}
    panel_res = client.post("/api/solar_panels/", headers=headers, json=panel_data)
    assert panel_res.status_code == 201
    panel_id = panel_res.json()["id"]

    # 2. Create a Battery
    battery_data = {"name": "ROI Test Battery", "purchase_cost_eur": 5000, "capacity_kwh": 10}
    battery_res = client.post("/api/batteries/", headers=headers, json=battery_data)
    assert battery_res.status_code == 201
    battery_id = battery_res.json()["id"]

    # 3. Create a Journal Entry
    journal_data = {
        "year": 2026, "month": 1,
        "grid_feed_in_low_kwh": 100, "feed_in_tariff_low_eur_kwh": 0.10,
        "solar_production_kwh": 300,
        "consumption_price_low_eur_kwh": 0.30, "consumption_price_high_eur_kwh": 0.50,
        "battery_discharge_kwh": 100,
        "car_journal_entries": []
    }
    journal_res = client.put("/api/journal/2026/1", headers=headers, json=journal_data)
    assert journal_res.status_code == 200

    # 4. Test Solar Panel ROI endpoint
    response = client.get(f"/api/roi/solar_panels/{panel_id}", headers=headers)
    assert response.status_code == 200
    content = response.json()
    assert content["total_investment"] == 10000
    assert content["total_savings"] > 0

    # 5. Test Battery ROI endpoint
    response = client.get(f"/api/roi/batteries/{battery_id}", headers=headers)
    assert response.status_code == 200
    content = response.json()
    assert content["total_investment"] == 5000
    assert content["total_savings"] > 0
