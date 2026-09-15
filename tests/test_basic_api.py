from random import randint
import pytest
import re
# REQUIRED_ELEMENT_IDS = [
#     "tx_phone_number",
#     "customer_id",
#     "transaction-customer-result",
#     "item_name",
#     "qty",
#     "unit_price",
#     "tx_note",
#     "tx-result",
# ]

# REQUIRED_JS_FUNCTIONS = [
#     "clearVerifiedTransactionCustomer",
#     "findTransactionCustomer",
#     "selectServiceCategory",
#     "applyCatalogItemPrice",
#     "createTransaction",
#     "listTransactions",
# ]
REQUIRED_ELEMENT_IDS = [
    "tx_phone_number",
    "customer_id",
    "transaction-customer-result",
    "item_name",
    "qty",
    "unit_price",
    "tx_note",
    "current-items-table",
    "current-spending",
    "total-spending",
]

REQUIRED_JS_FUNCTIONS = [
    "clearVerifiedTransactionCustomer",
    "findTransactionCustomer",
    "selectServiceCategory",
    "applyCatalogItemPrice",
    "addTransactionItem",
    "createTransaction",
    "initTransactionsPage",
]


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


def test_transaction_page_has_three_main_sections(client):
    response = client.get("/transactions")

    assert response.status_code == 200

    html = response.text

    assert html.count(
        'class="card transaction-section"'
    ) == 3

    # 第一區：查詢客戶
    assert 'id="tx_phone_number"' in html
    assert 'id="customer_id"' in html

    # 第二區：四個消費分類
    assert 'data-category="剪"' in html
    assert 'data-category="洗"' in html
    assert 'data-category="染"' in html
    assert 'data-category="燙"' in html

    # 第三區：此次消費與總消費
    assert 'id="current-spending"' in html
    assert 'id="total-spending"' in html
    assert 'id="current-items-table"' in html

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
            "password": "admin111",
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


@pytest.mark.parametrize(
    "invalid_phone_number",
    [
        "09138bc909",
        "091234567",
        "09123456789",
        "0812345678",
    ],
)
def test_create_customer_with_invalid_phone_number(
    client,
    auth_headers,
    invalid_phone_number,
):
    response = client.post(
        "/api/customers",
        headers=auth_headers,
        json={
            "name": "手機格式錯誤測試客戶",
            "phone_number": invalid_phone_number,
            "birthday": "1990-01-01",
        },
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "invalid_phone_number",
    [
        "0928a8b2b5",
        "091234567",
        "09123456789",
        "0812345678",
    ],
)
def test_update_customer_with_invalid_phone_number(
    client,
    auth_headers,
    sample_customer,
    invalid_phone_number,
):
    response = client.put(
        f"/api/customers/{sample_customer['id']}",
        headers=auth_headers,
        json={"phone_number": invalid_phone_number},
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

@pytest.mark.parametrize(
    "invalid_name",
    [
        "@@@",
        "!!!",
        "12345",
        "王小明@@",
    ],
)
def test_create_customer_with_invalid_name(
    client,
    auth_headers,
    invalid_name,
):
    response = client.post(
        "/api/customers",
        headers=auth_headers,
        json={
            "name": invalid_name,
            "phone_number": generate_phone_number(),
            "birthday": "1990-01-01",
        },
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "invalid_name",
    [
        "@@@",
        "!!!",
        "12345",
    ],
)
def test_update_customer_with_invalid_name(
    client,
    auth_headers,
    sample_customer,
    invalid_name,
):
    response = client.put(
        f"/api/customers/{sample_customer['id']}",
        headers=auth_headers,
        json={
            "name": invalid_name,
        },
    )

    assert response.status_code == 422


def remove_javascript_comments(source: str) -> str:
    """移除 JS 註解，避免把註解掉的舊函式誤認為有效函式。"""
    source = re.sub(r"/\*.*?\*/", "", source, flags=re.DOTALL)
    source = re.sub(r"^\s*//.*$", "", source, flags=re.MULTILINE)
    return source


def get_transaction_page_and_javascript(client):
    page_response = client.get("/transactions")
    js_response = client.get("/static/js/app.js")

    assert page_response.status_code == 200
    assert js_response.status_code == 200

    return page_response.text, js_response.text


def test_transaction_page_contains_required_elements(client):
    html, _ = get_transaction_page_and_javascript(client)

    for element_id in REQUIRED_ELEMENT_IDS:
        assert (
            f'id="{element_id}"' in html
        ), f"交易頁缺少 id={element_id} 的元素"


def test_four_service_categories_are_rendered(client):
    html, _ = get_transaction_page_and_javascript(client)

    for category in ("剪", "洗", "染", "燙"):
        assert category in html, f"交易頁缺少「{category}」分類"

    handler_count = html.count("selectServiceCategory(")

    assert handler_count >= 4, (
        "四大分類沒有全部綁定 selectServiceCategory()，"
        f"目前只找到 {handler_count} 個"
    )


def test_create_transaction_button_is_wired(client):
    html, _ = get_transaction_page_and_javascript(client)

    assert 'onclick="createTransaction()"' in html
    assert "新增消費" in html


def test_transaction_page_javascript_functions_exist(client):
    _, javascript = get_transaction_page_and_javascript(client)
    active_javascript = remove_javascript_comments(javascript)

    for function_name in REQUIRED_JS_FUNCTIONS:
        pattern = (
            rf"\b(?:async\s+)?function\s+"
            rf"{re.escape(function_name)}\s*\("
        )

        assert re.search(pattern, active_javascript), (
            f"app.js 缺少有效函式：{function_name}()，"
            "可能是函式被刪除、改名或註解掉"
        )


def test_required_javascript_functions_are_not_duplicated(client):
    _, javascript = get_transaction_page_and_javascript(client)
    active_javascript = remove_javascript_comments(javascript)

    for function_name in REQUIRED_JS_FUNCTIONS:
        pattern = (
            rf"\b(?:async\s+)?function\s+"
            rf"{re.escape(function_name)}\s*\("
        )

        definitions = re.findall(pattern, active_javascript)

        assert len(definitions) == 1, (
            f"{function_name}() 應該只有一個有效版本，"
            f"目前找到 {len(definitions)} 個"
        )


def test_html_handlers_match_javascript_functions(client):
    html, javascript = get_transaction_page_and_javascript(client)
    active_javascript = remove_javascript_comments(javascript)

    handlers_used_by_html = {
        function_name
        for function_name in REQUIRED_JS_FUNCTIONS
        if f"{function_name}(" in html
    }

    assert handlers_used_by_html, "交易頁沒有找到任何 JavaScript handler"

    for function_name in handlers_used_by_html:
        pattern = (
            rf"\b(?:async\s+)?function\s+"
            rf"{re.escape(function_name)}\s*\("
        )

        assert re.search(pattern, active_javascript), (
            f"HTML 有呼叫 {function_name}()，"
            "但是 app.js 沒有對應的有效函式"
        )