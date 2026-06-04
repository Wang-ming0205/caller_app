const API_PREFIX = "/api";

function token() {
  return localStorage.getItem("access_token");
}

function setMessage(text, isError = false) {
  const el = document.getElementById("message");
  if (!el) return;
  el.textContent = text;
  el.className = isError ? "message error" : "message";
}

function clearMessage() {
  const el = document.getElementById("message");
  if (el) el.className = "message hidden";
}

async function api(path, options = {}) {
  const headers = {"Content-Type": "application/json", ...(options.headers || {})};
  if (token()) headers.Authorization = `Bearer ${token()}`;
  const res = await fetch(`${API_PREFIX}${path}`, {...options, headers});
  const text = await res.text();
  let data = null;
  try { data = text ? JSON.parse(text) : null; } catch { data = text; }
  if (!res.ok) {
    const detail = data && data.detail ? data.detail : `HTTP ${res.status}`;
    throw new Error(detail);
  }
  return data;
}

async function checkLoginStatus(redirectWhenMissing = false) {
  const el = document.getElementById("login-status");
  if (!token()) {
    if (el) el.textContent = "尚未登入";
    if (redirectWhenMissing) window.location.href = "/login";
    return false;
  }
  try {
    const me = await api("/auth/me");
    if (el) el.textContent = `已登入：${me.username}（${me.role}）`;
    return true;
  } catch (err) {
    localStorage.removeItem("access_token");
    if (el) el.textContent = "登入已失效";
    if (redirectWhenMissing) window.location.href = "/login";
    return false;
  }
}

async function login() {
  clearMessage();
  try {
    const data = await api("/auth/login", {
      method: "POST",
      body: JSON.stringify({
        username: document.getElementById("username").value,
        password: document.getElementById("password").value,
      }),
    });
    localStorage.setItem("access_token", data.access_token);
    setMessage("登入成功");
    setTimeout(() => window.location.href = "/", 500);
  } catch (err) {
    setMessage(`登入失敗：${err.message}`, true);
  }
}

function logout() {
  localStorage.removeItem("access_token");
  window.location.href = "/login";
}

async function seedData() {
  clearMessage();
  try {
    const data = await api("/setup/seed", {method: "POST"});
    setMessage(JSON.stringify(data, null, 2));
  } catch (err) {
    setMessage(`建立測試資料失敗：${err.message}`, true);
  }
}

async function checkHealth() {
  const el = document.getElementById("health-result");
  try {
    const data = await fetch("/health").then(r => r.json());
    el.textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    el.textContent = err.message;
  }
}

async function createCustomer() {
  clearMessage();
  try {
    const payload = {
      name: document.getElementById("name").value,
      phone_number: document.getElementById("phone_number").value,
      gender: document.getElementById("gender").value || null,
      birthday: document.getElementById("birthday").value || null,
      note: document.getElementById("note").value || null,
    };
    const data = await api("/customers", {method: "POST", body: JSON.stringify(payload)});
    setMessage(`新增成功：${data.name} / ID ${data.id}`);
  } catch (err) {
    setMessage(`新增失敗：${err.message}`, true);
  }
}

async function searchCustomers() {
  clearMessage();
  const tbody = document.getElementById("customer-table");
  tbody.innerHTML = "";
  try {
    const q = encodeURIComponent(document.getElementById("q").value.trim());
    const data = await api(`/customers/search/list?q=${q}`);
    for (const c of data) {
      const tr = document.createElement("tr");
      tr.innerHTML = `<td>${c.id}</td><td>${escapeHtml(c.name)}</td><td>${escapeHtml(c.phone_number)}</td><td>${escapeHtml(c.gender || "")}</td><td>${escapeHtml(c.note || "")}</td><td><button onclick="customerSummary(${c.id})">摘要</button></td>`;
      tbody.appendChild(tr);
    }
  } catch (err) {
    setMessage(`查詢失敗：${err.message}`, true);
  }
}

async function customerSummary(id) {
  const el = document.getElementById("summary-result");
  try {
    const data = await api(`/customers/${id}/summary`);
    el.textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    el.textContent = err.message;
  }
}

async function createTransaction() {
  clearMessage();
  try {
    const payload = {
      customer_id: Number(document.getElementById("customer_id").value),
      note: document.getElementById("tx_note").value || null,
      items: [{
        item_name: document.getElementById("item_name").value,
        qty: Number(document.getElementById("qty").value || 1),
        unit_price: Number(document.getElementById("unit_price").value || 0),
      }],
    };
    const data = await api("/transactions", {method: "POST", body: JSON.stringify(payload)});
    setMessage(`消費新增成功：交易 ID ${data.id}，總金額 ${data.total_amount}`);
  } catch (err) {
    setMessage(`新增消費失敗：${err.message}`, true);
  }
}

async function listTransactions() {
  const el = document.getElementById("tx-result");
  try {
    const id = document.getElementById("tx_customer_id").value;
    const data = await api(`/transactions/customer/${id}`);
    el.textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    el.textContent = err.message;
  }
}

async function listUsers() {
  const tbody = document.getElementById("users-table");
  if (!tbody) return;
  tbody.innerHTML = "";
  try {
    const data = await api("/users");
    for (const u of data) {
      const tr = document.createElement("tr");
      tr.innerHTML = `<td>${u.id}</td><td>${escapeHtml(u.username)}</td><td>${escapeHtml(u.full_name || "")}</td><td>${escapeHtml(u.role)}</td><td>${u.is_active ? "是" : "否"}</td>`;
      tbody.appendChild(tr);
    }
  } catch (err) {
    setMessage(`讀取人員失敗：${err.message}`, true);
  }
}

async function createUser() {
  clearMessage();
  try {
    const payload = {
      username: document.getElementById("new_username").value,
      password: document.getElementById("new_password").value,
      full_name: document.getElementById("new_full_name").value || null,
      role: document.getElementById("new_role").value,
      is_active: true,
    };
    const data = await api("/users", {method: "POST", body: JSON.stringify(payload)});
    setMessage(`新增人員成功：${data.username}`);
    listUsers();
  } catch (err) {
    setMessage(`新增人員失敗：${err.message}`, true);
  }
}

async function loadMe() {
  const el = document.getElementById("me-result");
  if (!el) return;
  try {
    const data = await api("/users/me");
    el.textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    el.textContent = err.message;
  }
}

function escapeHtml(value) {
  return String(value).replace(/[&<>'"]/g, ch => ({"&":"&amp;","<":"&lt;",">":"&gt;","'":"&#039;","\"":"&quot;"}[ch]));
}
