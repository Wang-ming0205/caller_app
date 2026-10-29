# Caller App

> 🚧 持續開發中（Work in Progress）

## 專案介紹

Caller App 是我利用工作之餘持續開發的客戶管理系統（CRM），使用 FastAPI 建置。

專案最初以理髮店的會員與消費紀錄管理為發想，目前逐步擴充為通用的客戶管理系統，並持續導入 Service Layer、權限管理、自動化測試與雲端部署等工程實務。

## 線上網站

- 🌐 Website：https://caller-app-norr.onrender.com
- 📖 Swagger API 文件：https://caller-app-norr.onrender.com/docs

## 功能特色

- JWT 身分驗證
- 角色權限管理（Admin / Manager / Staff）
- 客戶資料新增、查詢、修改與刪除
- 客戶消費紀錄與消費項目管理
- CSV / Excel 批次匯入客戶
- CSV 匯出客戶資料
- 支援西元與民國生日格式匯入
- Audit Log 操作紀錄
- RESTful API
- HTML、Bootstrap 與 JavaScript 前端介面

## 使用技術

| 類別 | 技術 |
|------|------|
| Backend | Python、FastAPI |
| ORM | SQLAlchemy |
| 資料驗證 | Pydantic |
| 身分驗證 | JWT |
| Frontend | HTML、CSS、Bootstrap、JavaScript |
| Database | PostgreSQL（Supabase）、SQLite |
| Testing | pytest |
| Deployment | Render |
| Monitoring | UptimeRobot |
| Version Control | Git / GitHub |

## 專案架構

```text
caller_app/
├── app/
│   ├── api/          # API Router 與請求處理
│   ├── core/         # 設定、資料庫連線與安全性
│   ├── models/       # SQLAlchemy Model
│   ├── schemas/      # Pydantic Schema
│   ├── services/     # 商業邏輯（Service Layer）
│   ├── utils/        # 共用工具
│   └── web/          # HTML / CSS / JavaScript
│
├── docs/             # 專案文件
├── scripts/          # 資料初始化、匯入與維護工具
├── tests/            # pytest 自動化測試
│
├── requirements.txt  # Python 套件依賴
├── README.md
└── run.py
```

## 系統架構

```text
Browser / API Client
        │
        ▼
FastAPI Router
        │
        ▼
Service Layer
        │
        ▼
SQLAlchemy ORM
        │
        ▼
PostgreSQL / SQLite
```

- Router：接收請求，整合資料驗證、身分驗證與權限檢查。
- Service Layer：處理商業邏輯。
- SQLAlchemy ORM：處理資料庫查詢與資料寫入。
- 前端：透過 JavaScript 呼叫 API，呈現與更新畫面。

## 快速開始

### 1. 建立虛擬環境

在專案根目錄執行：

```bash
python -m venv .venv
```

### 2. 啟用虛擬環境

Windows PowerShell：

```powershell
.\.venv\Scripts\Activate.ps1
```

Linux / macOS：

```bash
source .venv/bin/activate
```

### 3. 安裝套件

```bash
python -m pip install -r requirements.txt
```

### 4. 設定環境

啟動前，請依照 `docs/` 內的說明設定資料庫連線與應用程式需要的環境變數。

### 5. 啟動應用程式

```bash
python run.py
```

啟動後可開啟：

- 網站：http://localhost:8000
- Swagger：http://localhost:8000/docs

## 測試

本專案使用 pytest 執行自動化測試，測試程式位於 `tests/`。

執行前請先啟用虛擬環境、安裝套件，並依測試設定使用獨立的測試資料庫，避免影響正式資料。

### 執行全部測試

在專案根目錄執行：

```bash
python -m pytest
```

### 顯示詳細測試結果

```bash
python -m pytest -v
```

### 顯示精簡測試結果

```bash
python -m pytest -q
```

### 依名稱篩選測試

例如，執行名稱包含 `customer` 的測試：

```bash
python -m pytest -k customer -v
```

實際測試案例與涵蓋範圍請參考 `tests/`；測試環境與相關說明請參考 `docs/`。

## 本機開發用預設帳號

以下帳號供本機開發與測試使用，是否建立取決於資料初始化設定。

| 帳號 | 密碼 | 權限 |
|------|------|------|
| admin | admin123 | Admin |
| manager | manager123 | Manager |
| staff | staff123 | Staff |

> 正式部署時應更換預設帳密，不應將這些帳號作為公開網站的共用登入帳號。

## API 範例

### 身分驗證

```http
POST /api/auth/login
GET  /api/auth/me
```

### 客戶管理

```http
GET    /api/customers
POST   /api/customers
PUT    /api/customers/{id}
DELETE /api/customers/{id}
```

### 消費紀錄

```http
POST /api/transactions
GET  /api/transactions/customer/{id}
```

完整端點、請求格式與回應內容請參考 Swagger API 文件。

## 部署與監控

### Render

使用 Render 部署 FastAPI 應用程式，正式環境資料庫使用 Supabase PostgreSQL。

### UptimeRobot

使用 UptimeRobot 定期發送 HTTP 請求，監控網站是否正常回應，並降低服務因閒置而休眠的機會。

- 官網：https://uptimerobot.com/

## 後續規劃

- [x] 基本 pytest API 測試
- [x] CSV / Excel 批次匯入客戶
- [x] CSV 匯出客戶
- [x] Excel 匯出客戶
- [x] Audit Log 操作紀錄
- [ ] 增加測試涵蓋範圍
- [ ] Alembic 資料庫版本管理
- [ ] Docker 容器化
- [ ] GitHub Actions 自動化測試與部署
- [ ] Dashboard 統計頁面
- [ ] 預約管理
- [ ] 多店家資料隔離（Multi Tenant）

## 開發紀錄

本專案使用 Git 進行版本控制，透過 Commit 記錄功能新增、問題修復與架構調整，並持續部署至 Render。

## 專案文件

詳細文件請參考 `docs/` 資料夾，包含部署說明、PostgreSQL 設定、測試指南與其他開發紀錄。
