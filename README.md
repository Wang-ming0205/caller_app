# Caller App

> 🚧 持續開發中（Work in Progress）

## 專案介紹

這個專案是我利用工作之餘持續開發的 FastAPI 個人作品。

最初以 理髮店 為發想，目前逐步重構為可擴充的客戶管理系統，並持續導入 Service Layer、權限管理、PostgreSQL、Render 部署、測試與其他工程實務。

一套使用 **FastAPI** 開發的客戶管理系統（CRM）。
- 🌐 Website：
  https://caller-app-norr.onrender.com

- 📖 Swagger：
  https://caller-app-norr.onrender.com/docs

目前包含：
## 功能特色

- JWT 身分驗證
- 權限管理（Admin / Manager / Staff）
- Customer CRUD
- Transaction CRUD
- RESTful API
- HTML + Bootstrap 前端
- PostgreSQL / SQLite
- Render 部署
---


# 使用技術（Tech Stack）

### Backend
- Python
- FastAPI
- SQLAlchemy
- Pydantic
- JWT Authentication

### Frontend
- HTML
- Bootstrap
- JavaScript

### Database
- PostgreSQL
- SQLite

### Deployment
- Render

---
# 專案架構
```
caller_app/
│
├── app/
│   ├── api/          # API Router
│   ├── core/         # 設定、資料庫、安全性
│   ├── models/       # SQLAlchemy Model
│   ├── schemas/      # Pydantic Schema
│   ├── services/     # 商業邏輯 (Business Logic)
│   ├── utils/        # 共用工具
│   └── web/          # HTML / CSS / JavaScript
│
├── docs/             # 專案文件
├── scripts/          # 維護工具(seed、匯入等等)
├── tests/            # pytest(單元測試)
│
├── README.md
└── run.py
```

---
# 快速開始
建立虛擬環境
```bash
python -m venv .venv
```

Windows
```bash
.venv\Scripts\activate
```

Linux / macOS
```bash
source .venv/bin/activate
```
安裝套件
```bash
pip install -r requirements.txt
```
啟動
```bash
python run.py
```

---
# 預設帳號

| 帳號 | 密碼 | 權限 |
|------|------|------|
| admin | admin123 | Admin |
| manager | manager123 | Manager |
| staff | staff123 | Staff |
---

# API 範例
登入
```
POST /api/auth/login
GET  /api/auth/me
```
客戶
```
GET    /api/customers
POST   /api/customers
PUT    /api/customers/{id}
DELETE /api/customers/{id}
```

交易
```
POST /api/transactions
GET  /api/transactions/customer/{id}
```

---
# 系統架構
```
Browser / API Client
        │
        ▼
API Router
        │
        ▼
Service Layer
        │
        ▼
SQLAlchemy Model
        │
        ▼
PostgreSQL / SQLite
```

---
# 後續規劃（Roadmap）
- [ ] pytest 單元測試
- [ ] Alembic Migration
- [ ] Docker
- [ ] GitHub Actions (CI/CD)
- [ ] Dashboard
- [ ] Excel / CSV 匯入匯出
- [ ] 多店家（Multi Tenant）
- [ ] Audit Log

## 開發紀錄
本專案採用 Git 進行版本控制，持續透過 Commit 紀錄功能新增、重構與架構調整，並同步部署至 Render。
