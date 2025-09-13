from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app import crud

def test_read_root(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_login(client: TestClient):
    # The startup event should have created the admin user
    response = client.post(
        "/api/auth/login",
        data={"username": "admin", "password": "admin"},
    )
    assert response.status_code == 200
    json_response = response.json()
    assert "access_token" in json_response
    assert json_response["token_type"] == "bearer"
