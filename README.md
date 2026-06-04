# Barbershop CRM：API + HTML + 外部裝置可連版本

這版包含：

- FastAPI API：`/api/...`
- Swagger API 文件：`/docs`
- HTML 頁面：`app/web/templates/`
- CSS / JS：`app/web/static/`
- 同 Wi-Fi 手機 / 其他電腦可連：`host=0.0.0.0`
- 健康檢查：`/health`

## 1. 啟動

Windows：

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python run.py
```

Mac / Linux：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python run.py
```

## 2. 本機開網站

```txt
http://127.0.0.1:8000/
```

## 3. 手機或另一台電腦開網站

手機與電腦要連同一個 Wi-Fi。先查你電腦 IP，例如：

```bat
ipconfig
```

找到 IPv4，例如：

```txt
192.168.1.23
```

手機開：

```txt
http://192.168.1.23:8000/
```

API 文件：

```txt
http://192.168.1.23:8000/docs
```

健康檢查：

```txt
http://192.168.1.23:8000/health
```

## 4. Windows 防火牆

如果手機打不開，通常是防火牆擋 8000 port。
用系統管理員 PowerShell 執行：

```powershell
New-NetFirewallRule -DisplayName "FastAPI 8000" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow
```

## 5. 測試帳號

先到登入頁按「建立測試資料 / 預設帳號」，或呼叫：

```txt
POST /api/setup/seed
```

預設帳密：

```txt
admin / admin123
manager / manager123
staff / staff123
```

## 6. API 路由

建議外部 call 使用 `/api` 前綴：

```txt
POST /api/auth/login
GET  /api/auth/me
POST /api/customers
GET  /api/customers/search/list?q=王
GET  /api/customers/{id}/summary
POST /api/transactions
GET  /api/transactions/customer/{customer_id}
GET  /api/users
POST /api/users
GET  /api/users/me
```

舊版無 `/api` 前綴的路由也保留，避免原本測試壞掉。

## 7. 目錄結構

```txt
app/
├── api/                 # JSON API
├── core/                # 設定、DB、安全
├── models/              # SQLAlchemy models
├── schemas/             # Pydantic schemas
├── web/
│   ├── pages.py         # HTML page routes
│   ├── templates/       # Jinja2 HTML templates
│   └── static/          # CSS / JS
└── main.py
```

## 8. 上線注意

正式上線前，請修改 `.env`：

```txt
ENV=prod
SECRET_KEY=換成很長很亂的字串
ENABLE_SEED=false
RELOAD=false
```

SQLite 可以測試；正式多人使用建議換 PostgreSQL。
