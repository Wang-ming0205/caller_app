from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def login(username="admin", password="admin111"):
    response = client.post(
        "/api/auth/login",
        json={
            "username": username,
            "password": password,
        },
    )

    assert response.status_code == 200
    return response.json()["access_token"]


def test_change_password_wrong_old_password():
    token = login()

    response = client.put(
        "/api/auth/me/password",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "old_password": "wrong_password",
            "new_password": "newpassword123",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Old password is incorrect"