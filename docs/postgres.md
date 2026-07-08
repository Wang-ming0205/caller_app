# PostgreSQL
## Driver（資料庫驅動）
本專案使用 PostgreSQL 的新版驅動：
```text
psycopg[binary]
```
搭配 SQLAlchemy 使用。
---

## SQLAlchemy URL
連線字串請使用：
```text
postgresql+psycopg://...
```
請勿使用：
```text
postgresql+psycopg2://...
```
除非專案真的需要使用 `psycopg2`。

---

## Common Errors（常見錯誤）
### ModuleNotFoundError: psycopg
**錯誤原因**
找不到 `psycopg` 套件，通常是尚未安裝 PostgreSQL Driver。

**解決方法**
安裝：
```bash
pip install "psycopg[binary]"
```
或更新：
```bash
pip install -r requirements.txt
```
---

### ImportError: undefined symbol: _PyInterpreterState_Get
**錯誤原因**
`psycopg2-binary` 與 **Python 3.14** 不相容，因此 Render 部署時會發生 ImportError。
例如：
```text
ImportError: ... undefined symbol: _PyInterpreterState_Get
```

**解決方法**
1. 將 `requirements.txt` 中：
```text
psycopg2-binary
```
改為：
```text
psycopg[binary]
```

2. SQLAlchemy 連線字串改成：
```text
postgresql+psycopg://...
```

3. 重新部署（Deploy）即可。
---

## Notes（備註）
本專案目前採用：
- Python 3.14
- SQLAlchemy 2.x
- psycopg[binary]
此組合可正常部署於 Render。