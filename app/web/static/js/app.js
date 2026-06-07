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
  showLoading();

  try {
    const headers = {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    };

    if (token()) headers.Authorization = `Bearer ${token()}`;

    const res = await fetch(`${API_PREFIX}${path}`, {
      ...options,
      headers,
    });

    const text = await res.text();

    let data = null;
    try {
      data = text ? JSON.parse(text) : null;
    } catch {
      data = text;
    }

    if (!res.ok) {
      const detail = data && data.detail ? data.detail : `HTTP ${res.status}`;
      throw new Error(detail);
    }

    return data;
  } finally {
    await new Promise(resolve =>
      setTimeout(resolve , 1000)
  );
    hideLoading();
  }
}

function hasSwal() {
  return typeof Swal !== "undefined";
}

function showLoading(title = "讀取中...") {
  if (!hasSwal()) return;

  Swal.fire({
    title,
    allowOutsideClick: false,
    allowEscapeKey: false,
    showConfirmButton: false,
    didOpen: () => {
      Swal.showLoading();
    },
  });
}

function hideLoading() {
  if (!hasSwal()) return;
  Swal.close();
}

async function showSuccess(title, text = "") {
  if (hasSwal()) {
    await Swal.fire({
      icon: "success",
      title,
      text,
      timer: 1200,
      showConfirmButton: false,
    });
  } else {
    setMessage(text ? `${title}：${text}` : title);
  }
}

function showError(title, err) {
  const text = err?.message || String(err);

  if (hasSwal()) {
    Swal.fire({
      icon: "error",
      title,
      text,
    });
  } else {
    setMessage(`${title}：${text}`, true);
  }
}

async function confirmAction(title, text = "此操作無法復原") {
  if (hasSwal()) {
    const result = await Swal.fire({
      title,
      text,
      icon: "warning",
      showCancelButton: true,
      confirmButtonText: "確定",
      cancelButtonText: "取消",
    });

    return result.isConfirmed;
  }

  return confirm(title);
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

async function initHome() {
  const ok = await checkLoginStatus(true);
  if (ok) {
    loadLatestCustomers();
  }
}

async function createCustomer() {
  clearMessage();

  try {
    const payload = {
      name: document.getElementById("name").value.trim(),
      phone_number: document.getElementById("phone_number").value.trim(),
      gender: document.getElementById("gender").value || null,
      birthday: document.getElementById("birthday").value || null,
      note: document.getElementById("note").value || null,
    };

    const data = await api("/customers", {
      method: "POST",
      body: JSON.stringify(payload),
    });

    await showSuccess('新增成功',`${data.name} / ID ${data.id}`);
    clearCustomerForm();
    loadLatestCustomers();

  } catch (err) {
    showError("新增失敗",err);
  }
}

async function loadLatestCustomers() {
  clearMessage();

  const tbody = document.getElementById("customer-table");
  if (!tbody) return;

  try {
    const data = await api("/customers/");
    renderCustomerTable(data);
  } catch (err) {
    setMessage(`讀取最新客戶失敗：${err.message}`, true);
  }
}

async function searchCustomers() {
  clearMessage();

  const q = document.getElementById("q").value.trim();

  if (!q) {
    loadLatestCustomers();
    return;
  }

  try {
    const data = await api(`/customers/search/list?q=${encodeURIComponent(q)}`);
    renderCustomerTable(data);
  } catch (err) {
    setMessage(`查詢失敗：${err.message}`, true);
  }
}

function renderCustomerTable(customers) {
  const tbody = document.getElementById("customer-table");
  if (!tbody) return;

  tbody.innerHTML = "";

  for (const c of customers) {
    const tr = document.createElement("tr");

    tr.innerHTML = `
      <td>${c.id}</td>
      <td><input id="name-${c.id}" value="${escapeHtml(c.name)}"></td>
      <td><input id="phone-${c.id}" value="${escapeHtml(c.phone_number)}"></td>
      <td>
        <select id="gender-${c.id}">
          <option value="" ${!c.gender ? "selected" : ""}>未填</option>
          <option value="男" ${c.gender === "男" ? "selected" : ""}>男</option>
          <option value="女" ${c.gender === "女" ? "selected" : ""}>女</option>
        </select>
      </td>
      <td><input id="note-${c.id}" value="${escapeHtml(c.note || "")}"></td>
      <td>
        <button onclick="updateCustomer(${c.id})">儲存</button>
        <button onclick="customerSummary(${c.id})">摘要</button>
        <button onclick="deleteCustomer(${c.id})">刪除</button>
      </td>
    `;

    tbody.appendChild(tr);
  }
}

async function updateCustomer(id) {
  clearMessage();

  try {
    const payload = {
      name: document.getElementById(`name-${id}`).value.trim(),
      phone_number: document.getElementById(`phone-${id}`).value.trim(),
      gender: document.getElementById(`gender-${id}`).value || null,
      note: document.getElementById(`note-${id}`).value || null,
    };

    const data = await api(`/customers/${id}`, {
      method: "PUT",
      body: JSON.stringify(payload),
    });

    await showSuccess("修改成功",data.name);
    loadLatestCustomers();

  } catch (err) {
    showError("修改失敗", err);
  }
}

async function deleteCustomer(id) {
  clearMessage();

    const ok = await confirmAction("確定刪除？");
    if (!ok) return;

    try {
      await api(`/customers/${id}`, {
        method: "DELETE",
      });

      await showSuccess("刪除成功");
      loadLatestCustomers();

    } catch (err) {
      showError("刪除失敗", err);
    }
  }

async function customerSummary(id) {
  const el = document.getElementById("summary-result");
  if (!el) return;

  try {
    const data = await api(`/customers/${id}/summary`);
    el.textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    el.textContent = err.message;
  }
}

function clearCustomerForm() {
  document.getElementById("name").value = "";
  document.getElementById("phone_number").value = "";
  document.getElementById("gender").value = "";
  document.getElementById("birthday").value = "";
  document.getElementById("note").value = "";
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

async function changeMyPassword() {
  clearMessage();

  const oldPassword = document.getElementById("old_password").value;
  const newPassword = document.getElementById("new_password").value;
  const confirmPassword = document.getElementById("confirm_password").value;

  if (!oldPassword || !newPassword || !confirmPassword) {
    showError("欄位未完成", "請完整輸入所有密碼欄位");
    return;
  }

  if (newPassword !== confirmPassword) {
    showError("密碼不一致", "新密碼與確認新密碼不一致");
    return;
  }

  try {
    await api("/users/me/password", {
      method: "PUT",
      body: JSON.stringify({
        old_password: oldPassword,
        new_password: newPassword,
      }),
    });

    await showSuccess("密碼修改成功，請重新登入");
    localStorage.removeItem("access_token");

    setTimeout(() => {
      window.location.href = "/login";
    }, 800);

  } catch (err) {
    showError("密碼修改失敗",err);
  }
}


