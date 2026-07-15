def test_change_password_wrong_old_password(client, auth_headers):
    response = client.put(
        "/api/auth/me/password",
        headers=auth_headers,
        json={
            "old_password": "wrong_password",
            "new_password": "newpassword123",
        },
    )

    assert response.status_code == 400

    data = response.json()

    assert data["detail"] == "Old password is incorrect"