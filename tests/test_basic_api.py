# from random import randint

# def generate_phone_number():
#     """
#     Generate a random Taiwanese mobile phone number.
#     產生隨機台灣手機號碼，降低測試資料重複的機率。
#     """
#     return f"09{randint(10000000, 99999999)}"

# # ====================
# # Home API
# # ====================
# def test_home(client):
#     response = client.get("/")

#     assert response.status_code == 200


# # ====================
# # Auth API
# # ====================
# def test_login_without_data(client):
#     response = client.post(
#         "/api/auth/login",
#         json={
#             "username": "",
#             "password": "",
#         },
#     )

#     assert response.status_code in (400, 401, 422)

# def test_login_success(client):
#     response = client.post(
#         "/api/auth/login",
#         json={
#             "username": "admin",
#             "password": "admin123",
#         },
#     )
#     assert response.status_code == 200
#     data = response.json()
#     assert "access_token" in data
#     assert data["access_token"]

# def test_login_wrong_password(client):
#     response = client.post(
#         "/api/auth/login",
#         json={
#             "username": "admin",
#             "password": "wrong_password",
#         },
#     )
#     assert response.status_code in (400, 401)

# def test_change_password_wrong_old_password(client, auth_headers):
#     response = client.put(
#         "/api/auth/me/password",
#         headers=auth_headers,
#         json={
#             "old_password": "wrong_password",
#             "new_password": "newpassword123",
#         },
#     )
#     assert response.status_code == 400
#     data = response.json()
#     assert data["detail"] == "Old password is incorrect"

# # ====================
# # Customers API
# # ====================
# def test_customers_requires_login(client):
#     """
#     Verify that unauthenticated users cannot access customer data.
#     驗證未登入使用者無法取得客戶資料。
#     """
#     response = client.get("/api/customers/")
#     assert response.status_code in (401, 403)

# def test_get_customers(client, auth_headers):
#     """
#     Verify that authenticated users can retrieve the customer list.
#     驗證已登入使用者可以取得客戶清單。
#     """
#     response = client.get(
#         "/api/customers/",
#         headers=auth_headers,
#     )
#     assert response.status_code == 200
#     assert isinstance(response.json(), list)

# def test_get_customer_by_id(client, auth_headers, sample_customer):
#     response = client.get(
#         f"/api/customers/{sample_customer['id']}",
#         headers=auth_headers,
#     )
#     assert response.status_code == 200
#     data = response.json()
#     assert data["id"] == sample_customer["id"]
#     assert data["name"] == sample_customer["name"]
#     assert data["phone_number"] == sample_customer["phone_number"]

# def test_create_customer(client, auth_headers):
#     """
#     Verify that a customer can be created successfully.
#     驗證可以成功建立客戶。
#     """
#     customer_data = {
#         "name": "pytest 測試客戶",
#         "phone_number": generate_phone_number(),
#         "note": "由 pytest 建立",
#     }
#     response = client.post(
#         "/api/customers",
#         headers=auth_headers,
#         json=customer_data,
#     )
#     assert response.status_code == 200
#     data = response.json()
#     assert "id" in data
#     assert data["name"] == customer_data["name"]
#     assert data["phone_number"] == customer_data["phone_number"]

# def test_get_customer_by_phone(client, auth_headers):
#     """
#     Verify that a customer can be retrieved by phone number.
#     驗證可以透過手機號碼查詢客戶。
#     """
#     phone_number = generate_phone_number()
#     customer_data = {
#         "name": "手機查詢測試客戶",
#         "phone_number": phone_number,
#         "note": "測試依手機號碼查詢",
#     }
#     create_response = client.post(
#         "/api/customers",
#         headers=auth_headers,
#         json=customer_data,
#     )
#     assert create_response.status_code == 200
#     response = client.get(
#         f"/api/customers/by-phone/{phone_number}",
#         headers=auth_headers,
#     )
#     assert response.status_code == 200
#     data = response.json()
#     assert data["name"] == customer_data["name"]
#     assert data["phone_number"] == phone_number

# def test_update_customer(client, auth_headers, sample_customer):
#     updated_customer_data = {
#         "name": "pytest 修改後客戶",
#         "phone_number": generate_phone_number(),
#         "note": "由 pytest 修改",
#     }
#     response = client.put(
#         f"/api/customers/{sample_customer['id']}",
#         headers=auth_headers,
#         json=updated_customer_data,
#     )
#     assert response.status_code == 200
#     data = response.json()
#     assert data["id"] == sample_customer["id"]
#     assert data["name"] == updated_customer_data["name"]
#     assert data["phone_number"] == updated_customer_data["phone_number"]
#     assert data["note"] == updated_customer_data["note"]

# def test_delete_customer(client, auth_headers, sample_customer):
#     delete_response = client.delete(
#         f"/api/customers/{sample_customer['id']}",
#         headers=auth_headers,
#     )
#     assert delete_response.status_code in (200, 204)
#     get_response = client.get(
#         f"/api/customers/{sample_customer['id']}",
#         headers=auth_headers,
#     )
#     assert get_response.status_code == 404

# def test_get_nonexistent_customer(client, auth_headers):
#     """
#     Verify that requesting a nonexistent customer returns HTTP 404.
#     驗證查詢不存在的客戶時回傳 HTTP 404。
#     """
#     response = client.get(
#         "/api/customers/999999999",
#         headers=auth_headers,
#     )
#     assert response.status_code == 404

# def test_create_customer_with_duplicate_phone(client, auth_headers):
#     """
#     Verify that duplicate phone numbers are rejected.
#     驗證系統會拒絕重複的手機號碼。
#     """
#     phone_number = generate_phone_number()
#     customer_data = {
#         "name": "重複手機測試客戶",
#         "phone_number": phone_number,
#         "note": "測試重複手機",
#     }
#     first_response = client.post(
#         "/api/customers",
#         headers=auth_headers,
#         json=customer_data,
#     )
#     assert first_response.status_code == 200
#     second_response = client.post(
#         "/api/customers",
#         headers=auth_headers,
#         json=customer_data,
#     )
#     assert second_response.status_code == 400
#     assert (
#         second_response.json()["detail"]
#         == "Phone number already exists for this user"
#     )

# def test_create_customer_without_name(client, auth_headers):
#     """
#     Verify that an empty customer name is rejected.
#     驗證系統會拒絕空字串姓名。
#     """
#     customer_data = {
#         "name": "",
#         "phone_number": generate_phone_number(),
#         "note": "缺少姓名測試",
#     }
#     response = client.post(
#         "/api/customers",
#         headers=auth_headers,
#         json=customer_data,
#     )
#     assert response.status_code == 422

# def test_create_customer_with_blank_name(client, auth_headers):
#     """
#     Verify that a whitespace-only customer name is rejected.
#     驗證系統會拒絕只有空白字元的姓名。
#     """
#     customer_data = {
#         "name": "   ",
#         "phone_number": generate_phone_number(),
#         "note": "只有空白的姓名",
#     }
#     response = client.post(
#         "/api/customers",
#         headers=auth_headers,
#         json=customer_data,
#     )
#     assert response.status_code == 422

# # ====================
# # Transactions API
# # ====================
# def test_transactions_requires_login(client):
#     response = client.post(
#         "/api/transactions",
#         json={
#             "customer_id": 999999999,
#             "items": [
#                 {
#                     "item_name": "未登入測試",
#                     "qty": 1,
#                     "unit_price": 500,
#                 }
#             ],
#         },
#     )
#     assert response.status_code in (401, 403)

# def test_create_transaction_without_customer(client, auth_headers):
#     response = client.post(
#         "/api/transactions",
#         headers=auth_headers,
#         json={
#             "items": [
#                 {
#                     "item_name": "散客剪髮",
#                     "qty": 1,
#                     "unit_price": 500,
#                 }
#             ],
#             "note": "未指定客戶的散客消費",
#         },
#     )
#     assert response.status_code in (200, 201)
#     data = response.json()
#     assert data["customer_id"] is None
#     assert float(data["total_amount"]) == 500
#     assert len(data["items"]) == 1

# def test_create_transaction(
#     client,
#     auth_headers,
#     sample_customer,
# ):
#     response = client.post(
#         "/api/transactions",
#         headers=auth_headers,
#         json={
#             "customer_id": sample_customer["id"],
#             "items": [
#                 {
#                     "item_name": "剪髮",
#                     "qty": 1,
#                     "unit_price": 500,
#                 }
#             ],
#         },
#     )
#     assert response.status_code in (200, 201)
#     data = response.json()
#     assert data["customer_id"] == sample_customer["id"]
#     assert float(data["total_amount"]) == 500
#     assert len(data["items"]) == 1

# def test_create_transaction_for_nonexistent_customer(
#     client,
#     auth_headers,
# ):
#     response = client.post(
#         "/api/transactions",
#         headers=auth_headers,
#         json={
#             "customer_id": 999999999,
#             "items": [
#                 {
#                     "item_name": "剪髮",
#                     "qty": 1,
#                     "unit_price": 500,
#                 }
#             ],
#         },
#     )
#     assert response.status_code in (400, 404)

# def test_create_transaction_with_invalid_amount(
#     client,
#     auth_headers,
#     sample_customer,
# ):
#     response = client.post(
#         "/api/transactions",
#         headers=auth_headers,
#         json={
#             "customer_id": sample_customer["id"],
#             "items": [
#                 {
#                     "item_name": "錯誤金額測試",
#                     "qty": 1,
#                     "unit_price": -100,
#                 }
#             ],
#         },
#     )
#     assert response.status_code == 422

# #同名不同電話可以新增
# def test_create_customers_with_same_name_but_different_phone(
#     client,
#     auth_headers,
# ):
#     first_customer = {
#         "name": "王小明",
#         "phone_number": "0911111111",
#         "note": "第一位同名客戶",
#     }
#     second_customer = {
#         "name": "王小明",
#         "phone_number": "0922222222",
#         "note": "第二位同名客戶",
#     }
#     first_response = client.post(
#         "/api/customers",
#         json=first_customer,
#         headers=auth_headers,
#     )
#     second_response = client.post(
#         "/api/customers",
#         json=second_customer,
#         headers=auth_headers,
#     )
#     assert first_response.status_code == 200
#     assert second_response.status_code == 200
#     assert first_response.json()["name"] == "王小明"
#     assert second_response.json()["name"] == "王小明"
#     assert (
#         first_response.json()["phone_number"]
#         != second_response.json()["phone_number"]
#     )

from random import randint


def generate_phone_number():
    """
    Generate a random Taiwanese mobile phone number.
    產生隨機台灣手機號碼，降低測試資料重複的機率。
    """
    return f"09{randint(10000000, 99999999)}"


# ====================
# Home API
# ====================


def test_home(client):
    response = client.get("/")

    assert response.status_code == 200


def test_transaction_page_uses_phone_and_allows_free_item_input(client):
    # response = client.get("/transactions")

    # assert response.status_code == 200
    # assert 'id="tx_phone_number"' in response.text
    # assert 'id="item_name"' in response.text
    # assert 'id="catalog_item_id"' not in response.text
    
    #new_version
    response = client.get("/transactions")
    assert response.status_code == 200
    html = response.text
    # 使用手機查詢客戶
    assert 'id="tx_phone_number"' in html
    # 客戶 ID 由查詢結果保存，不需要手動輸入
    assert 'id="customer_id"' in html
    assert 'type="hidden"' in html
    # 消費項目改成既有項目的下拉選單
    assert 'id="catalog_item_id"' in html
    assert 'onchange="applyCatalogItemPrice()"' in html
    assert '請選擇消費項目' in html
    # 不再允許直接輸入任意項目名稱
    assert 'id="item_name"' not in html
    assert 'catalog-item-suggestions' not in html


def test_customer_create_page_marks_core_fields_required(client):
    response = client.get("/customers/new")

    assert response.status_code == 200
    assert 'id="name" placeholder="王小明" required' in response.text
    assert 'id="phone_number" placeholder="0912345678" required' in response.text
    assert 'id="birthday" type="date" required' in response.text


# ====================
# Auth API
# ====================


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
            "password": "admin123",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["access_token"]


def test_login_wrong_password(client):
    response = client.post(
        "/api/auth/login",
        json={
            "username": "admin",
            "password": "wrong_password",
        },
    )

    assert response.status_code in (400, 401)


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


# ====================
# Customers API
# ====================


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


def test_get_customer_by_id(client, auth_headers, sample_customer):
    response = client.get(
        f"/api/customers/{sample_customer['id']}",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == sample_customer["id"]
    assert data["name"] == sample_customer["name"]
    assert data["phone_number"] == sample_customer["phone_number"]


def test_create_customer(client, auth_headers):
    """
    Verify that a customer can be created successfully.
    驗證可以成功建立客戶。
    """
    customer_data = {
        "name": "pytest 測試客戶",
        "phone_number": generate_phone_number(),
        "birthday": "1990-01-01",
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
        "birthday": "1990-01-01",
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


def test_update_customer(client, auth_headers, sample_customer):
    updated_customer_data = {
        "name": "pytest 修改後客戶",
        "phone_number": generate_phone_number(),
        "note": "由 pytest 修改",
    }

    response = client.put(
        f"/api/customers/{sample_customer['id']}",
        headers=auth_headers,
        json=updated_customer_data,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == sample_customer["id"]
    assert data["name"] == updated_customer_data["name"]
    assert data["phone_number"] == updated_customer_data["phone_number"]
    assert data["note"] == updated_customer_data["note"]


def test_delete_customer(client, auth_headers, sample_customer):
    delete_response = client.delete(
        f"/api/customers/{sample_customer['id']}",
        headers=auth_headers,
    )

    assert delete_response.status_code in (200, 204)

    get_response = client.get(
        f"/api/customers/{sample_customer['id']}",
        headers=auth_headers,
    )

    assert get_response.status_code == 404


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
        "birthday": "1990-01-01",
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
        == "Phone number already exists"
    )


def test_create_customers_with_same_name(client, auth_headers):
    """同名客戶可以存在，只限制手機號碼不可重複。"""
    customer_name = "同名測試客戶"

    first_response = client.post(
        "/api/customers",
        headers=auth_headers,
        json={
            "name": customer_name,
            "phone_number": generate_phone_number(),
            "birthday": "1990-01-01",
        },
    )
    second_response = client.post(
        "/api/customers",
        headers=auth_headers,
        json={
            "name": customer_name,
            "phone_number": generate_phone_number(),
            "birthday": "1992-02-02",
        },
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 200


def test_update_customer_with_duplicate_phone(
    client,
    auth_headers,
    sample_customer,
):
    other_customer_response = client.post(
        "/api/customers",
        headers=auth_headers,
        json={
            "name": "另一位客戶",
            "phone_number": generate_phone_number(),
            "birthday": "1991-02-03",
        },
    )
    assert other_customer_response.status_code == 200

    response = client.put(
        f"/api/customers/{sample_customer['id']}",
        headers=auth_headers,
        json={
            "phone_number": other_customer_response.json()["phone_number"],
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Phone number already exists"


def test_create_customer_without_birthday(client, auth_headers):
    response = client.post(
        "/api/customers",
        headers=auth_headers,
        json={
            "name": "缺少生日測試客戶",
            "phone_number": generate_phone_number(),
        },
    )

    assert response.status_code == 422


def test_create_customer_without_name(client, auth_headers):
    """
    Verify that an empty customer name is rejected.
    驗證系統會拒絕空字串姓名。
    """
    customer_data = {
        "name": "",
        "phone_number": generate_phone_number(),
        "birthday": "1990-01-01",
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
        "birthday": "1990-01-01",
        "note": "只有空白的姓名",
    }

    response = client.post(
        "/api/customers",
        headers=auth_headers,
        json=customer_data,
    )

    assert response.status_code == 422


# ====================
# Transactions API
# ====================


def test_transactions_requires_login(client):
    response = client.post(
        "/api/transactions",
        json={
            "customer_id": 999999999,
            "items": [
                {
                    "item_name": "未登入測試",
                    "qty": 1,
                    "unit_price": 500,
                }
            ],
        },
    )

    assert response.status_code in (401, 403)


def test_create_transaction_without_customer(client, auth_headers):
    response = client.post(
        "/api/transactions",
        headers=auth_headers,
        json={
            "items": [
                {
                    "item_name": "散客剪髮",
                    "qty": 1,
                    "unit_price": 500,
                }
            ],
            "note": "未指定客戶的散客消費",
        },
    )

    assert response.status_code == 422


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
            "items": [
                {
                    "item_name": "剪髮",
                    "qty": 1,
                    "unit_price": 500,
                }
            ],
        },
    )

    assert response.status_code in (200, 201)

    data = response.json()

    assert data["customer_id"] == sample_customer["id"]
    assert float(data["total_amount"]) == 500
    assert len(data["items"]) == 1


def test_create_transaction_for_nonexistent_customer(
    client,
    auth_headers,
):
    response = client.post(
        "/api/transactions",
        headers=auth_headers,
        json={
            "customer_id": 999999999,
            "items": [
                {
                    "item_name": "剪髮",
                    "qty": 1,
                    "unit_price": 500,
                }
            ],
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
            "items": [
                {
                    "item_name": "錯誤金額測試",
                    "qty": 1,
                    "unit_price": -100,
                }
            ],
        },
    )

    assert response.status_code == 422
