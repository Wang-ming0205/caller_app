from random import randint

def generate_phone_number():
    """
    Generate a random Taiwanese mobile phone number.
    產生隨機台灣手機號碼，降低測試資料重複的機率。
    """
    return f"09{randint(10000000, 99999999)}"


def test_customers_requires_login(client):
    """
    Verify that unauthenticated users cannot access customer data.
    驗證未登入使用者無法取得客戶資料。
    """
    response = client.get("/api/customers/")

    assert response.status_code in (401, 403)


def test_get_customers(client, auth_headers):
    """
    Verify that authenticated users can retrieve the customer list.
    驗證已登入使用者可以取得客戶清單。
    """
    response = client.get(
        "/api/customers/",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_customer(client, auth_headers):
    """
    Verify that a customer can be created successfully.
    驗證可以成功建立客戶。
    """
    customer_data = {
        "name": "pytest 測試客戶",
        "phone_number": generate_phone_number(),
        "note": "由 pytest 建立",
    }

    response = client.post(
        "/api/customers",
        headers=auth_headers,
        json=customer_data,
    )

    assert response.status_code == 200

    data = response.json()

    assert "id" in data
    assert data["name"] == customer_data["name"]
    assert data["phone_number"] == customer_data["phone_number"]


def test_get_customer_by_phone(client, auth_headers):
    """
    Verify that a customer can be retrieved by phone number.
    驗證可以透過手機號碼查詢客戶。
    """
    phone_number = generate_phone_number()

    customer_data = {
        "name": "手機查詢測試客戶",
        "phone_number": phone_number,
        "note": "測試依手機號碼查詢",
    }

    create_response = client.post(
        "/api/customers",
        headers=auth_headers,
        json=customer_data,
    )

    assert create_response.status_code == 200

    response = client.get(
        f"/api/customers/by-phone/{phone_number}",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == customer_data["name"]
    assert data["phone_number"] == phone_number


def test_get_nonexistent_customer(client, auth_headers):
    """
    Verify that requesting a nonexistent customer returns HTTP 404.
    驗證查詢不存在的客戶時回傳 HTTP 404。
    """
    response = client.get(
        "/api/customers/999999999",
        headers=auth_headers,
    )

    assert response.status_code == 404


def test_create_customer_with_duplicate_phone(client, auth_headers):
    """
    Verify that duplicate phone numbers are rejected.
    驗證系統會拒絕重複的手機號碼。
    """
    phone_number = generate_phone_number()

    customer_data = {
        "name": "重複手機測試客戶",
        "phone_number": phone_number,
        "note": "測試重複手機",
    }

    first_response = client.post(
        "/api/customers",
        headers=auth_headers,
        json=customer_data,
    )

    assert first_response.status_code == 200

    second_response = client.post(
        "/api/customers",
        headers=auth_headers,
        json=customer_data,
    )

    assert second_response.status_code == 400
    assert (
        second_response.json()["detail"]
        == "Phone number already exists for this user"
    )


def test_create_customer_without_name(client, auth_headers):
    """
    Verify that an empty customer name is rejected.
    驗證系統會拒絕空字串姓名。
    """
    customer_data = {
        "name": "",
        "phone_number": generate_phone_number(),
        "note": "缺少姓名測試",
    }

    response = client.post(
        "/api/customers",
        headers=auth_headers,
        json=customer_data,
    )

    assert response.status_code == 422


def test_create_customer_with_blank_name(client, auth_headers):
    """
    Verify that a whitespace-only customer name is rejected.
    驗證系統會拒絕只有空白字元的姓名。
    """
    customer_data = {
        "name": "   ",
        "phone_number": generate_phone_number(),
        "note": "只有空白的姓名",
    }

    response = client.post(
        "/api/customers",
        headers=auth_headers,
        json=customer_data,
    )

    assert response.status_code == 422