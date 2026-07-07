from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_login_without_data():
    response = client.post(
        "/api/auth/login",
        json={
            "username": "",
            "password": ""
        },
    )

    assert response.status_code in (400, 401, 422)

