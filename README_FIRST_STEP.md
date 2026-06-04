# First Step：登入 + user_id 資料隔離

這版已完成第一優先：

- JWT 登入保留 `/auth/login`
- `customers` 新增 `owner_user_id`
- 新增 customer 時會自動綁目前登入者
- 查 customer、電話查詢、search、summary、transactions 都會檢查資料擁有者
- `admin` 可以看全部
- `manager` / `staff` 只能看自己的資料

## 重要

如果你之前已經跑過舊版，請先刪除舊的 SQLite 檔：

```bash
barbershop.db
```

原因：`Base.metadata.create_all()` 只會建立新表，不會自動幫舊表新增 `owner_user_id` 欄位。
正式專案會用 Alembic migration，但今天先不做那層。

## 啟動

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

打開：

```text
http://127.0.0.1:8000/docs
```

## 測試流程

### 1. 建立假資料

POST：

```text
/setup/seed
```

會建立三個帳號：

```text
admin / admin123
manager / manager123
staff / staff123
```

### 2. 登入 manager

POST：

```text
/auth/login
```

Body：

```json
{
  "username": "manager",
  "password": "manager123"
}
```

複製 `access_token`。

### 3. Swagger 授權

右上角 `Authorize`：

```text
Bearer 你的_token
```

### 4. 測試資料隔離

manager 可以查到自己名下的 customer。
staff 查 manager 的 customer 會回：

```json
{
  "detail": "Customer not found"
}
```

這是刻意設計成 404，不用 403，避免暴露「別人的 customer id 是否存在」。

## 今日完成標準

你今天只要確認三件事：

1. `/auth/login` 可以登入
2. `POST /customers` 新增資料會出現 `owner_user_id`
3. 不同帳號查不到彼此的 customer

做到這裡，第一步就結束。
