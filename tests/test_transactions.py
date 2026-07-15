
def test_transactions_requires_login(client):
    response = client.get("/api/transactions")

    assert response.status_code in (401, 403, 404, 405)


def test_create_transaction(
    client,
    auth_headers,
    sample_customer,
):

    response = client.post(
        "/api/transactions",
        headers=auth_headers,
        json={
            "customer_id": sample_customer["id"],
            "amount": 500,
        },
    )

    assert response.status_code in (200, 201)

    data = response.json()

    assert data["customer_id"] == sample_customer["id"]
    assert float(data["amount"]) == 500


def test_create_transaction_for_nonexistent_customer(
    client,
    auth_headers,
):
    response = client.post(
        "/api/transactions",
        headers=auth_headers,
        json={
            "customer_id": 999999999,
            "amount": 500,
        },
    )

    assert response.status_code in (400, 404)

def test_create_transaction_with_invalid_amount(
    client,
    auth_headers,
    sample_customer,
):

    response = client.post(
        "/api/transactions",
        headers=auth_headers,
        json={
            "customer_id": sample_customer["id"],
            "amount": -100,
        },
    )

    assert response.status_code in (400, 422)