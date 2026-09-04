#高破壞性測試
from datetime import date
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, func, select
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.core.security import hash_password
from app.main import app
from app.models.audit_log import AuditLog
from app.models.catalog_item import CatalogItem
from app.models.customer import Customer
from app.models.transaction import Transaction, TransactionItem
from app.models.user import User


RESET_URL = "/api/admin/reset-data"
ADMIN_PASSWORD = "admin123"
CONFIRMATION_TEXT = "DELETE ALL DATA"


@pytest.fixture
def reset_test_environment(tmp_path):
    """
    每個測試建立獨立的臨時 SQLite。

    不使用：
    - barbershop.db
    - test_barbershop.db
    - Supabase PostgreSQL
    """
    database_path = tmp_path / "admin_reset_test.db"

    test_engine = create_engine(
        f"sqlite:///{database_path}",
        connect_args={"check_same_thread": False},
    )

    @event.listens_for(test_engine, "connect")
    def enable_sqlite_foreign_keys(dbapi_connection, _):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    TestSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine,
    )

    Base.metadata.create_all(bind=test_engine)

    # 建立三個必須保留的基本帳號。
    with TestSessionLocal() as db:
        db.add_all(
            [
                User(
                    username="admin",
                    password_hash=hash_password(ADMIN_PASSWORD),
                    full_name="Administrator",
                    role="admin",
                    is_active=True,
                ),
                User(
                    username="manager",
                    password_hash=hash_password("manager123"),
                    full_name="Manager",
                    role="manager",
                    is_active=True,
                ),
                User(
                    username="staff",
                    password_hash=hash_password("staff123"),
                    full_name="Staff",
                    role="staff",
                    is_active=True,
                ),
            ]
        )
        db.commit()

    def override_get_db():
        db = TestSessionLocal()

        try:
            yield db
        finally:
            db.close()

    previous_override = app.dependency_overrides.get(get_db)
    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as client:
            yield client, TestSessionLocal
    finally:
        if previous_override is None:
            app.dependency_overrides.pop(get_db, None)
        else:
            app.dependency_overrides[get_db] = previous_override

        test_engine.dispose()


def login_headers(
    client: TestClient,
    username: str,
    password: str,
) -> dict[str, str]:
    """
    使用真正的登入 API 取得 JWT，
    避免測試自行猜測 token 的 subject 格式。
    """
    response = client.post(
        "/api/auth/login",
        data={
            "username": username,
            "password": password,
        },
    )

    # 如果你的登入 API 使用 JSON，就改用 JSON 再送一次。
    if response.status_code == 422:
        response = client.post(
            "/api/auth/login",
            json={
                "username": username,
                "password": password,
            },
        )

    assert response.status_code == 200, response.text

    token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}",
    }


def seed_application_data(SessionLocal):
    """建立完整資料鏈，確認 Foreign Key 刪除順序正確。"""
    with SessionLocal() as db:
        admin = db.scalar(
            select(User).where(User.username == "admin")
        )
        staff = db.scalar(
            select(User).where(User.username == "staff")
        )

        extra_user = User(
            username="temporary_user",
            password_hash=hash_password("temporary123"),
            full_name="Temporary User",
            role="staff",
            is_active=True,
        )
        db.add(extra_user)
        db.flush()

        customer = Customer(
            name="格式化測試客戶",
            phone_number="0912345678",
            owner_user_id=admin.id,
            gender="other",
            birthday=date(2000, 1, 1),
            note="這筆資料應該被刪除",
        )
        db.add(customer)
        db.flush()

        catalog_item = CatalogItem(
            name="格式化測試項目",
            default_price=Decimal("500.00"),
            description="這筆資料應該被刪除",
            is_active=True,
        )
        db.add(catalog_item)

        transaction = Transaction(
            customer_id=customer.id,
            stylist_user_id=staff.id,
            total_amount=Decimal("500.00"),
            note="格式化測試消費",
        )
        db.add(transaction)
        db.flush()

        transaction_item = TransactionItem(
            transaction_id=transaction.id,
            item_name="格式化測試項目",
            qty=1,
            unit_price=Decimal("500.00"),
            subtotal=Decimal("500.00"),
        )
        db.add(transaction_item)

        # 故意讓 AuditLog 指向即將被刪除的額外帳號，
        # 驗證 Service 必須先刪 AuditLog 再刪 User。
        audit_log = AuditLog(
            user_id=extra_user.id,
            action="CREATE",
            target_type="customer",
            target_id=customer.id,
            detail={"source": "admin reset test"},
        )
        db.add(audit_log)

        db.commit()


def get_count(SessionLocal, model) -> int:
    with SessionLocal() as db:
        return db.scalar(
            select(func.count()).select_from(model)
        )


def test_reset_requires_login(reset_test_environment):
    client, _ = reset_test_environment

    response = client.post(
        RESET_URL,
        json={
            "password": ADMIN_PASSWORD,
            "confirmation": CONFIRMATION_TEXT,
        },
    )

    assert response.status_code == 403


@pytest.mark.parametrize("username", ["manager", "staff"])
def test_non_admin_cannot_reset_data(
    reset_test_environment,
    username,
):
    client, _ = reset_test_environment

    response = client.post(
        RESET_URL,
        headers=login_headers(
            client,
            username,
            f"{username}123",
        ),
        json={
            "password": "any-password",
            "confirmation": CONFIRMATION_TEXT,
        },
    )

    assert response.status_code == 403


def test_wrong_confirmation_does_not_delete_data(
    reset_test_environment,
):
    client, SessionLocal = reset_test_environment
    seed_application_data(SessionLocal)

    response = client.post(
        RESET_URL,
        headers=login_headers(
            client,
            "admin",
            ADMIN_PASSWORD,
        ),
        json={
            "password": ADMIN_PASSWORD,
            "confirmation": "DELETE",
        },
    )

    assert response.status_code == 400
    assert get_count(SessionLocal, Customer) == 1
    assert get_count(SessionLocal, Transaction) == 1
    assert get_count(SessionLocal, User) == 4


def test_wrong_password_does_not_delete_data(
    reset_test_environment,
):
    client, SessionLocal = reset_test_environment
    seed_application_data(SessionLocal)

    response = client.post(
        RESET_URL,
        headers=login_headers(
            client,
            "admin",
            ADMIN_PASSWORD,
        ),
        json={
            "password": "wrong-password",
            "confirmation": CONFIRMATION_TEXT,
        },
    )

    assert response.status_code == 400
    assert get_count(SessionLocal, Customer) == 1
    assert get_count(SessionLocal, Transaction) == 1
    assert get_count(SessionLocal, User) == 4


def test_admin_can_reset_data_and_preserve_basic_users(
    reset_test_environment,
):
    client, SessionLocal = reset_test_environment
    seed_application_data(SessionLocal)

    with SessionLocal() as db:
        original_password_hashes = dict(
            db.execute(
                select(User.username, User.password_hash).where(
                    User.username.in_(
                        ("admin", "manager", "staff")
                    )
                )
            ).all()
        )

    response = client.post(
        RESET_URL,
        headers=login_headers(
            client,
            "admin",
            ADMIN_PASSWORD,
        ),
        json={
            "password": ADMIN_PASSWORD,
            "confirmation": CONFIRMATION_TEXT,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["message"] == (
        "Application data reset successfully"
    )
    assert body["preserved_users"] == [
        "admin",
        "manager",
        "staff",
    ]

    assert body["deleted"] == {
        "transaction_items": 1,
        "transactions": 1,
        "customers": 1,
        "catalog_items": 1,
        "audit_logs": 1,
        "users": 1,
    }

    assert get_count(SessionLocal, TransactionItem) == 0
    assert get_count(SessionLocal, Transaction) == 0
    assert get_count(SessionLocal, Customer) == 0
    assert get_count(SessionLocal, CatalogItem) == 0
    assert get_count(SessionLocal, AuditLog) == 0

    with SessionLocal() as db:
        remaining_users = db.execute(
            select(User).order_by(User.username)
        ).scalars().all()

    assert [user.username for user in remaining_users] == [
        "admin",
        "manager",
        "staff",
    ]

    remaining_password_hashes = {
        user.username: user.password_hash
        for user in remaining_users
    }

    # 確認格式化沒有修改三個基本帳號的密碼。
    assert remaining_password_hashes == original_password_hashes