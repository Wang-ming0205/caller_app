from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter(tags=["web"])
templates = Jinja2Templates(directory="app/web/templates")

@router.get("/")
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request, "title": "首頁"})

@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request, "title": "登入"})

@router.get("/customers")
def customers_page(request: Request):
    return templates.TemplateResponse("customers/list.html", {"request": request, "title": "客戶管理"})

@router.get("/customers/new")
def customer_create_page(request: Request):
    return templates.TemplateResponse("customers/create.html", {"request": request, "title": "新增客戶"})

@router.get("/items")
def items_page(request: Request):
    return templates.TemplateResponse("items/list.html", {"request": request, "title": "消費項目"})

@router.get("/transactions")
def transactions_page(request: Request):
    return templates.TemplateResponse("customers/transactions.html", {"request": request, "title": "新增消費"})

@router.get("/users")
def users_page(request: Request):
    return templates.TemplateResponse("users/list.html", {"request": request, "title": "人員管理"})

@router.get("/account")
def account_page(request: Request):
    return templates.TemplateResponse("users/account.html", {"request": request, "title": "帳號設定"})
