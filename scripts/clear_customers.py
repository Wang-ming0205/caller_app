import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.database import SessionLocal
from app.models.customer import Customer


def main():
    confirm = input("⚠️ 即將刪除所有客戶資料，輸入 YES 才繼續：")

    if confirm != "YES":
        print("已取消")
        return

    db = SessionLocal()

    try:
        count = db.query(Customer).count()
        db.query(Customer).delete()
        db.commit()

        print(f"✅ 已刪除 {count} 位客戶")

    except Exception as e:
        db.rollback()
        print(f"❌ 刪除失敗：{e}")

    finally:
        db.close()


if __name__ == "__main__":
    main()