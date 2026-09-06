import os
from pathlib import Path
from uuid import uuid4

import pytest


# 必須放在所有 app imports 之前，確保 pytest 只使用測試資料庫。
PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEST_DB_PATH = PROJECT_ROOT / "test_barbershop.db"
TEST_DATABASE_URL = f"sqlite:///{TEST_DB_PATH.as_posix()}"

os.environ["DATABASE_URL"] = TEST_DATABASE_URL
os.environ["ENV"] = "test"
os.environ["SECRET_KEY"] = "pytest-test-secret-key"


from fastapi.testclient import TestClient

from app.core.database import Base, SessionLocal, engine
from app.core.security import hash_password
from app.main import app
from app.models.user import User


def create_test_users():
    """建立測試需要的基本帳號，不載入正式 seed 資料。"""
    with SessionLocal() as db:
        admin = User(
            username="admin",
            password_hash=hash_password("admin111"),
            full_name="Test Admin",
            role="admin",
        )
        manager = User(
            username="manager",
            password_hash=hash_password("manager123"),
            full_name="Test Manager",
            role="manager",
        )
        staff = User(
            username="staff",
            password_hash=hash_password("staff123"),
            full_name="Test Staff",
            role="staff",
        )

        db.add_all([admin, manager, staff])
        db.commit()


@pytest.fixture(scope="session", autouse=True)
def cleanup_test_database():
    """整個 pytest session 結束後刪除測試資料庫。"""
    yield

    Base.metadata.drop_all(bind=engine)
    engine.dispose()

    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()


@pytest.fixture(autouse=True)
def reset_test_database():
    """每個測試開始前重建資料表與基本帳號。"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    create_test_users()
    yield


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def admin_token(client):
    response = client.post(
        "/api/auth/login",
        json={
            "username": "admin",
            "password": "admin111",
        },
    )

    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def auth_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def sample_customer(client, auth_headers):
    """建立交易測試使用的臨時客戶，手機固定為 10 位純數字。"""
    unique_digits = str(uuid4().int)[-8:]

    response = client.post(
        "/api/customers",
        headers=auth_headers,
        json={
            "name": f"交易測試客戶_{unique_digits}",
            "phone_number": f"09{unique_digits}",
            "birthday": "1990-01-01",
        },
    )

    assert response.status_code in (200, 201)

    data = response.json()
    assert "id" in data
    return data
