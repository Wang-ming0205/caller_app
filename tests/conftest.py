import pytest
from fastapi.testclient import TestClient
from app.main import app
from uuid import uuid4



@pytest.fixture
def client():
    """
    Create a new FastAPI TestClient for each test.

    為每一個測試建立全新的 TestClient，
    確保每個測試案例彼此獨立，不共用 Client。
    """
    with TestClient(app) as test_client:
        yield test_client




@pytest.fixture
def admin_token(client):
    """
    Log in as the default administrator and return a JWT access token.

    使用預設管理員帳號登入，
    回傳 JWT Access Token，供其他測試共用。
    """
    response = client.post(
        "/api/auth/login",
        json={
            "username": "admin",
            "password": "admin123",
        },
    )

    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def auth_headers(admin_token):
    """
    Build Authorization headers for authenticated API requests.

    建立需要登入驗證時使用的 Authorization Header，
    避免每個測試都重複組 JWT Header。
    """
    return {
        "Authorization": f"Bearer {admin_token}"
    }

@pytest.fixture
def sample_customer(client, auth_headers):
    """
    Create a temporary customer for transaction tests.


    建立一位測試用客戶，
    供 Transaction（交易）相關測試共用。

    A unique phone number is generated every time to avoid
    duplicate phone number conflicts.

    每次建立都會產生唯一的手機號碼，
    避免測試時因重複手機號碼而失敗。
    """

    # Generate a unique value for testing.
    # 產生唯一識別值，避免測試資料重複。
    unique_value = uuid4().hex[:8]

    response = client.post(
        "/api/customers",
        headers=auth_headers,
        json={
            "name": f"交易測試客戶_{unique_value}",
            "phone_number": f"09{unique_value[:8]}",
        },
    )

    assert response.status_code in (200, 201)

    data = response.json()
    assert "id" in data

    return data

