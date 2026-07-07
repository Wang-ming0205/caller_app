import random
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.database import SessionLocal
from app.models.customer import Customer
from app.models.user import User


def main(count: int = 100):
    db = SessionLocal()

    try:
        user = db.query(User).first()

        if not user:
            print("❌ 沒有任何 user，請先建立帳號或執行 seed")
            return

        for i in range(count):
            customer = Customer(
                name=f"測試客戶{i + 1}",
                phone_number=f"09{random.randint(10000000, 99999999)}",
                owner_user_id=user.id,
                gender=random.choice(["男", "女", None]),
                note="script 自動新增的測試資料",
            )
            db.add(customer)

        db.commit()
        print(f"✅ 已新增 {count} 位測試客戶，owner_user_id={user.id}")

    except Exception as e:
        db.rollback()
        print(f"❌ 新增失敗：{e}")

    finally:
        db.close()


if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    main(count)