def test_login_without_data(client):
    response = client.post(
        "/api/auth/login",
        json={
            "username": "",
            "password": "",
        },
    )

    assert response.status_code in (400, 401, 422)



def test_login_success(client):
    response = client.post(
        "/api/auth/login",
        json={
            "username": "admin",
            "password": "admin111",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["access_token"]
    data = response.json()

    assert "access_token" in data
    assert data["access_token"]