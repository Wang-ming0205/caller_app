from sqlalchemy import select
from app.core.database import SessionLocal
from app.models.customer import Customer
from app.models.transaction import Transaction, TransactionItem


def create_transaction(
    client,
    auth_headers,
    customer_id,
    item_name="剪髮",
    qty=1,
    unit_price=500,
):
    response = client.post(
        "/api/transactions",
        headers=auth_headers,
        json={
            "customer_id": customer_id,
            "note": "刪除一致性測試",
            "items": [
                {
                    "item_name": item_name,
                    "qty": qty,
                    "unit_price": unit_price,
                }
            ],
        },
    )

    assert response.status_code in (200, 201), response.text

    data = response.json()
    assert "id" in data

    return data


def get_transaction_and_items(transaction_id):
    """使用新的 Session 直接查測試資料庫。"""
    with SessionLocal() as db:
        transaction = db.get(Transaction, transaction_id)

        items = list(
            db.execute(
                select(TransactionItem).where(
                    TransactionItem.transaction_id
                    == transaction_id
                )
            ).scalars()
        )

        if transaction is None:
            return None, items

        transaction_data = {
            "id": transaction.id,
            "customer_id": transaction.customer_id,
            "total_amount": float(
                transaction.total_amount
            ),
        }

        item_data = [
            {
                "id": item.id,
                "transaction_id": item.transaction_id,
                "item_name": item.item_name,
                "qty": item.qty,
                "unit_price": float(item.unit_price),
                "subtotal": float(item.subtotal),
            }
            for item in items
        ]

        return transaction_data, item_data


def test_delete_customer_preserves_transaction_history(
    client,
    auth_headers,
    sample_customer,
):
    transaction = create_transaction(
        client=client,
        auth_headers=auth_headers,
        customer_id=sample_customer["id"],
        item_name="剪髮",
        unit_price=500,
    )

    transaction_before, items_before = (
        get_transaction_and_items(transaction["id"])
    )

    assert transaction_before is not None
    assert (
        transaction_before["customer_id"]
        == sample_customer["id"]
    )
    assert len(items_before) == 1
    assert items_before[0]["item_name"] == "剪髮"

    delete_response = client.delete(
        f"/api/customers/{sample_customer['id']}",
        headers=auth_headers,
    )

    assert delete_response.status_code in (
        200,
        204,
    ), delete_response.text

    customer_response = client.get(
        f"/api/customers/{sample_customer['id']}",
        headers=auth_headers,
    )

    assert customer_response.status_code == 404

    transaction_after, items_after = (
        get_transaction_and_items(transaction["id"])
    )

    # 刪除客戶後，歷史交易應保留。
    assert transaction_after is not None, (
        "刪除客戶後，歷史交易也被刪除了"
    )

    # 交易不能繼續指向已不存在的客戶。
    assert transaction_after["customer_id"] is None, (
        "刪除客戶後，Transaction.customer_id "
        "沒有被設為 NULL"
    )

    assert transaction_after["total_amount"] == 500.0

    # 交易項目也應保留。
    assert len(items_after) == 1
    assert items_after[0]["item_name"] == "剪髮"
    assert items_after[0]["qty"] == 1
    assert items_after[0]["unit_price"] == 500.0


def test_deleting_one_customer_does_not_affect_another_customer(
    client,
    auth_headers,
    sample_customer,
):
    second_customer_response = client.post(
        "/api/customers",
        headers=auth_headers,
        json={
            "name": "保留測試客戶",
            "phone_number": "0987654321",
            "birthday": "1990-01-01",
            "note": "不應被其他客戶刪除影響",
        },
    )

    assert second_customer_response.status_code in (
        200,
        201,
    ), second_customer_response.text

    second_customer = second_customer_response.json()

    first_transaction = create_transaction(
        client=client,
        auth_headers=auth_headers,
        customer_id=sample_customer["id"],
        item_name="剪髮",
        unit_price=500,
    )

    second_transaction = create_transaction(
        client=client,
        auth_headers=auth_headers,
        customer_id=second_customer["id"],
        item_name="染髮",
        unit_price=1200,
    )

    delete_response = client.delete(
        f"/api/customers/{sample_customer['id']}",
        headers=auth_headers,
    )

    assert delete_response.status_code in (
        200,
        204,
    ), delete_response.text

    with SessionLocal() as db:
        first_customer_in_db = db.get(
            Customer,
            sample_customer["id"],
        )

        second_customer_in_db = db.get(
            Customer,
            second_customer["id"],
        )

        first_transaction_in_db = db.get(
            Transaction,
            first_transaction["id"],
        )

        second_transaction_in_db = db.get(
            Transaction,
            second_transaction["id"],
        )

        first_items = list(
            db.execute(
                select(TransactionItem).where(
                    TransactionItem.transaction_id
                    == first_transaction["id"]
                )
            ).scalars()
        )

        second_items = list(
            db.execute(
                select(TransactionItem).where(
                    TransactionItem.transaction_id
                    == second_transaction["id"]
                )
            ).scalars()
        )

        assert first_customer_in_db is None

        assert second_customer_in_db is not None
        assert (
            second_customer_in_db.id
            == second_customer["id"]
        )

        assert first_transaction_in_db is not None
        assert (
            first_transaction_in_db.customer_id
            is None
        )

        assert second_transaction_in_db is not None
        assert (
            second_transaction_in_db.customer_id
            == second_customer["id"]
        )

        assert (
            float(second_transaction_in_db.total_amount)
            == 1200.0
        )

        assert len(first_items) == 1
        assert first_items[0].item_name == "剪髮"

        assert len(second_items) == 1
        assert second_items[0].item_name == "染髮"