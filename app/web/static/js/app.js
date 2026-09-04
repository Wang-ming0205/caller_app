// new version
const API_PREFIX = "/api";
let currentUser = null;

async function api(path, options = {}) {
  // 如果剛從其他頁面透過 goToPage() 跳轉過來，
  // 舊頁面已經顯示過「頁面載入中」，第一個初始化 API 就不要再顯示「讀取中」。
  const skipInitialLoading =
    options.showLoading !== false &&
    sessionStorage.getItem("page_navigation_loading") === "true";

  if (skipInitialLoading) {
    // 只略過新頁面的第一個 API，之後的新增、查詢、刪除仍會顯示「讀取中」。
    sessionStorage.removeItem("page_navigation_loading");
  }

  const shouldShowLoading =
    options.showLoading !== false && !skipInitialLoading;

  if (shouldShowLoading) {
    showLoading();
  }

  try {
    const headers = {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    };

    const currentToken = localStorage.getItem("access_token");

    if (currentToken) {
      headers.Authorization = `Bearer ${currentToken}`;
    }

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
      const detail =
        data && data.detail
          ? data.detail
          : `HTTP ${res.status}`;

      throw new Error(detail);
    }

    return data;
  } finally {
    if (shouldShowLoading) {
      hideLoading();
    }
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
    window.alert(
      text
        ? `${title}：${text}`
        : title,
    );
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
    window.alert(`${title}：${text}`);
  }
}

function showInfo(title, text = "") {
  if (hasSwal()) {
    Swal.fire({
      icon: "info",
      title,
      text,
    });
  } else {
    window.alert(
      text
        ? `${title}：${text}`
        : title,
    );
  }
}

async function confirmAction(
  title,
  text = "此操作無法復原",
) {
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

// ==================== 登入登出 ====================

function updateAdminResetTrigger(user = null) {
  const trigger =
    document.getElementById("admin-reset-trigger");

  if (!trigger) return;

  const isAccountPage =
    window.location.pathname === "/account";

  const isAdmin = user?.role === "admin";

  trigger.hidden = !(isAccountPage && isAdmin);
}

async function checkLoginStatus(
  redirectWhenMissing = true,
) {
  const el = document.getElementById("login-status");
  const currentToken =
    localStorage.getItem("access_token");

  if (!currentToken) {
    currentUser = null;

    if (el) {
      el.textContent = "尚未登入";
    }

    updateAuthButton(false);
    updateAdminResetTrigger();

    if (redirectWhenMissing) {
      goToPage("/login");
    }

    return false;
  }

  try {
    const me = await api(
      "/auth/me",
      { showLoading: false },
    );

    currentUser = me;

    if (el) {
      el.textContent =
        `已登入：${me.username}（${me.role}）`;
    }

    updateAuthButton(true);
    updateAdminResetTrigger(me);

    return true;
  } catch (err) {
    currentUser = null;
    localStorage.removeItem("access_token");

    if (el) {
      el.textContent = "登入已失效";
    }

    updateAuthButton(false);
    updateAdminResetTrigger();

    if (redirectWhenMissing) {
      window.location.href = "/login";
    }

    return false;
  }
}

async function login() {
  try {
    const data = await api("/auth/login", {
      method: "POST",
      body: JSON.stringify({
        username:
          document.getElementById("username").value,
        password:
          document.getElementById("password").value,
      }),
    });

    localStorage.setItem(
      "access_token",
      data.access_token,
    );

    await showSuccess("登入成功");
    goToPage("/");
  } catch (err) {
    showError("登入失敗", err);
  }
}

function logout() {
  currentUser = null;
  updateAdminResetTrigger();

  localStorage.removeItem("access_token");
  goToPage("/login");
}

// ==================== Admin 系統資料格式化 ====================

let adminResetClickCount = 0;
let adminResetClickTimer = null;
let isResettingApplicationData = false;

function handleAdminResetTrigger() {
  if (
    currentUser?.role !== "admin" ||
    isResettingApplicationData
  ) {
    return;
  }

  adminResetClickCount += 1;

  if (adminResetClickTimer) {
    clearTimeout(adminResetClickTimer);
  }

  if (adminResetClickCount >= 3) {
    adminResetClickCount = 0;
    adminResetClickTimer = null;

    showAdminResetDialog();
    return;
  }

  // 三次點擊必須在 1.5 秒內完成，逾時就重新計算。
  adminResetClickTimer = setTimeout(() => {
    adminResetClickCount = 0;
    adminResetClickTimer = null;
  }, 1500);
}

async function showAdminResetDialog() {
  if (
    !hasSwal() ||
    currentUser?.role !== "admin"
  ) {
    return;
  }

  const confirmationResult = await Swal.fire({
    icon: "warning",
    title: "確定要格式化系統資料？",
    html: `
      <p style="text-align:left; margin-bottom:.5rem;">
        這會永久刪除所有客戶、消費紀錄、消費項目、
        操作紀錄與額外帳號。
      </p>

      <p style="text-align:left;">
        系統只會保留
        <strong>admin、manager、staff</strong>
        三個基本帳號及其目前密碼。
      </p>

      <input
        id="reset-confirmation"
        class="swal2-input"
        autocomplete="off"
        placeholder="輸入 DELETE ALL DATA"
      >

      <input
        id="reset-password"
        type="password"
        class="swal2-input"
        autocomplete="current-password"
        placeholder="輸入目前 Admin 密碼"
      >
    `,
    showCancelButton: true,
    confirmButtonText: "永久刪除資料",
    cancelButtonText: "取消",
    confirmButtonColor: "#d33",
    focusConfirm: false,
    allowOutsideClick: false,

    preConfirm: () => {
      const confirmation = document
        .getElementById("reset-confirmation")
        .value
        .trim();

      const password = document
        .getElementById("reset-password")
        .value;

      if (confirmation !== "DELETE ALL DATA") {
        Swal.showValidationMessage(
          "請完整輸入 DELETE ALL DATA",
        );

        return false;
      }

      if (!password) {
        Swal.showValidationMessage(
          "請輸入目前 Admin 密碼",
        );

        return false;
      }

      return {
        confirmation,
        password,
      };
    },
  });

  if (!confirmationResult.isConfirmed) {
    return;
  }

  isResettingApplicationData = true;

  try {
    const data = await api(
      "/admin/reset-data",
      {
        method: "POST",
        body: JSON.stringify(
          confirmationResult.value,
        ),
      },
    );

    const deleted = data.deleted || {};

    await Swal.fire({
      icon: "success",
      title: "系統資料已格式化",
      html: `
        <div
          style="
            text-align:left;
            display:inline-block;
          "
        >
          客戶：${deleted.customers || 0}<br>
          消費紀錄：${deleted.transactions || 0}<br>
          消費明細：${deleted.transaction_items || 0}<br>
          消費項目：${deleted.catalog_items || 0}<br>
          操作紀錄：${deleted.audit_logs || 0}<br>
          額外帳號：${deleted.users || 0}
        </div>
      `,
      confirmButtonText: "完成",
      allowOutsideClick: false,
    });

    window.location.reload();
  } catch (err) {
    showError(
      "系統資料格式化失敗",
      err,
    );
  } finally {
    isResettingApplicationData = false;
  }
}

// ================== Admin 系統資料格式化結束 ==================

async function seedData() {
  try {
    const data = await api(
      "/setup/seed",
      {
        method: "POST",
      },
    );

    await showSuccess(
      "測試資料建立完成",
      data.message || "",
    );
  } catch (err) {
    showError(
      "建立測試資料失敗",
      err,
    );
  }
}

async function checkHealth() {
  const el =
    document.getElementById("health-result");

  try {
    const data = await fetch("/health")
      .then((response) => response.json());

    el.textContent =
      JSON.stringify(data, null, 2);
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

let isCreatingCustomer = false;

async function createCustomer() {
  if (isCreatingCustomer) return;

  isCreatingCustomer = true;

  try {
    const name = document
      .getElementById("name")
      .value
      .trim();

    const phoneNumber = document
      .getElementById("phone_number")
      .value
      .trim();

    const birthday =
      document.getElementById("birthday").value;

    if (
      !name ||
      !phoneNumber ||
      !birthday
    ) {
      showError(
        "欄位未完成",
        "請填寫姓名、手機與生日",
      );

      return;
    }

    const payload = {
      name,
      phone_number: phoneNumber,
      gender:
        document.getElementById("gender").value ||
        null,
      birthday,
      note:
        document.getElementById("note").value ||
        null,
    };

    const data = await api("/customers", {
      method: "POST",
      body: JSON.stringify(payload),
    });

    await showSuccess(
      "新增成功",
      `${data.name} / ID ${data.id}`,
    );

    clearCustomerForm();
    loadLatestCustomers();
  } catch (err) {
    showError("新增失敗", err);
  } finally {
    isCreatingCustomer = false;
  }
}

async function loadLatestCustomers() {
  const tbody =
    document.getElementById("customer-table");

  if (!tbody) return;

  try {
    const data = await api("/customers/");
    renderCustomerTable(data);
  } catch (err) {
    showError(
      "讀取最新客戶失敗",
      err,
    );
  }
}

async function searchCustomers() {
  const q = document
    .getElementById("q")
    .value
    .trim();

  if (!q) {
    loadLatestCustomers();
    return;
  }

  try {
    const data = await api(
      `/customers/search/list?q=${encodeURIComponent(q)}`,
    );

    renderCustomerTable(data);
  } catch (err) {
    showError("查詢失敗", err);
  }
}

function renderCustomerTable(customers) {
  const tbody =
    document.getElementById("customer-table");

  if (!tbody) return;

  tbody.innerHTML = "";

  for (const customer of customers) {
    const tr = document.createElement("tr");

    tr.innerHTML = `
      <td>${customer.id}</td>

      <td>
        <input
          id="name-${customer.id}"
          value="${escapeHtml(customer.name)}"
        >
      </td>

      <td>
        <input
          id="phone-${customer.id}"
          value="${escapeHtml(customer.phone_number)}"
        >
      </td>

      <td>
        <select id="gender-${customer.id}">
          <option
            value=""
            ${!customer.gender ? "selected" : ""}
          >
            未填
          </option>

          <option
            value="男"
            ${customer.gender === "男" ? "selected" : ""}
          >
            男
          </option>

          <option
            value="女"
            ${customer.gender === "女" ? "selected" : ""}
          >
            女
          </option>
        </select>
      </td>

      <td>
        <input
          id="note-${customer.id}"
          value="${escapeHtml(customer.note || "")}"
        >
      </td>

      <td>
        <button
          onclick="updateCustomer(${customer.id})"
        >
          儲存
        </button>

        <button
          onclick="customerSummary(${customer.id})"
        >
          摘要
        </button>

        <button
          onclick="deleteCustomer(${customer.id})"
        >
          刪除
        </button>
      </td>
    `;

    tbody.appendChild(tr);
  }
}

async function updateCustomer(id) {
  try {
    const payload = {
      name: document
        .getElementById(`name-${id}`)
        .value
        .trim(),

      phone_number: document
        .getElementById(`phone-${id}`)
        .value
        .trim(),

      gender:
        document.getElementById(`gender-${id}`)
          .value || null,

      note:
        document.getElementById(`note-${id}`)
          .value || null,
    };

    const data = await api(
      `/customers/${id}`,
      {
        method: "PUT",
        body: JSON.stringify(payload),
      },
    );

    await showSuccess(
      "修改成功",
      data.name,
    );

    loadLatestCustomers();
  } catch (err) {
    showError("修改失敗", err);
  }
}

async function deleteCustomer(id) {
  const ok =
    await confirmAction("確定刪除？");

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
  const el =
    document.getElementById("summary-result");

  if (!el) return;

  try {
    const data = await api(
      `/customers/${id}/summary`,
    );

    el.textContent =
      JSON.stringify(data, null, 2);
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

let isCreatingTransaction = false;

function clearVerifiedTransactionCustomer() {
  const customerId =
    document.getElementById("customer_id");

  const result =
    document.getElementById(
      "transaction-customer-result",
    );

  if (customerId) {
    customerId.value = "";
  }

  if (result) {
    result.textContent = "";
    result.classList.add("hidden");
  }
}

function showVerifiedTransactionCustomer(
  customer,
) {
  const customerId =
    document.getElementById("customer_id");

  const result =
    document.getElementById(
      "transaction-customer-result",
    );

  if (customerId) {
    customerId.value = customer.id;
  }

  if (result) {
    result.textContent =
      `已找到：${customer.name}／生日：` +
      `${customer.birthday || "未填"}`;

    result.classList.remove(
      "hidden",
      "error",
    );
  }
}

async function findTransactionCustomer() {
  const phoneNumber = document
    .getElementById("tx_phone_number")
    .value
    .trim();

  if (!phoneNumber) {
    clearVerifiedTransactionCustomer();

    showError(
      "欄位未完成",
      "請輸入客戶手機",
    );

    return null;
  }

  try {
    const customer = await api(
      `/customers/by-phone/${encodeURIComponent(phoneNumber)}`,
    );

    showVerifiedTransactionCustomer(customer);

    return customer;
  } catch (err) {
    clearVerifiedTransactionCustomer();
    showError("找不到客戶", err);

    return null;
  }
}

async function createTransaction() {
  if (isCreatingTransaction) return;

  const phoneNumber = document
    .getElementById("tx_phone_number")
    .value
    .trim();

  const catalogSelect =
    document.getElementById("catalog_item_id");

  const selectedItem =
    catalogSelect?.selectedOptions[0];

  const itemName =
    selectedItem?.dataset.name || "";

  const qty = Number(
    document.getElementById("qty").value,
  );

  const unitPrice = Number(
    document.getElementById("unit_price").value,
  );

  if (!phoneNumber || !itemName) {
    showError(
      "欄位未完成",
      "請填寫客戶手機並選擇消費項目",
    );

    return;
  }

  if (
    !Number.isInteger(qty) ||
    qty < 1 ||
    !Number.isFinite(unitPrice) ||
    unitPrice < 0
  ) {
    showError(
      "欄位格式錯誤",
      "數量至少為 1，單價不可小於 0",
    );

    return;
  }

  isCreatingTransaction = true;

  showLoading(
    "驗證客戶並新增消費中...",
  );

  try {
    const customer = await api(
      `/customers/by-phone/${encodeURIComponent(phoneNumber)}`,
      {
        showLoading: false,
      },
    );

    showVerifiedTransactionCustomer(customer);

    const payload = {
      customer_id: customer.id,

      note:
        document.getElementById("tx_note")
          .value || null,

      items: [
        {
          item_name: itemName,
          qty,
          unit_price: unitPrice,
        },
      ],
    };

    const data = await api(
      "/transactions",
      {
        method: "POST",
        body: JSON.stringify(payload),
        showLoading: false,
      },
    );

    hideLoading();

    await showSuccess(
      "消費新增成功",
      `交易 ID ${data.id}，總金額 ${data.total_amount}`,
    );

    document.getElementById(
      "tx_phone_number",
    ).value = "";

    catalogSelect.value = "";

    document.getElementById(
      "qty",
    ).value = "1";

    document.getElementById(
      "unit_price",
    ).value = "0";

    document.getElementById(
      "tx_note",
    ).value = "";

    clearVerifiedTransactionCustomer();
  } catch (err) {
    hideLoading();

    showError(
      "新增消費失敗",
      err,
    );
  } finally {
    isCreatingTransaction = false;
  }
}

async function listTransactions() {
  const el =
    document.getElementById("tx-result");

  const phoneNumber = document
    .getElementById("tx_history_phone")
    .value
    .trim();

  if (!phoneNumber) {
    el.textContent = "";

    showError(
      "欄位未完成",
      "請輸入客戶手機",
    );

    return;
  }

  showLoading("讀取消費紀錄中...");

  try {
    const customer = await api(
      `/customers/by-phone/${encodeURIComponent(phoneNumber)}`,
      {
        showLoading: false,
      },
    );

    const data = await api(
      `/transactions/customer/${customer.id}`,
      {
        showLoading: false,
      },
    );

    hideLoading();

    el.textContent =
      JSON.stringify(data, null, 2);
  } catch (err) {
    hideLoading();

    el.textContent = "";

    showError(
      "讀取消費紀錄失敗",
      err,
    );
  }
}

async function loadCatalogItems() {
  const tbody =
    document.getElementById(
      "catalog-items-table",
    );

  if (!tbody) return [];

  try {
    const data = await api("/items");

    tbody.innerHTML = "";

    for (const item of data) {
      const tr = document.createElement("tr");

      tr.innerHTML = `
        <td>${item.id}</td>
        <td>${escapeHtml(item.name)}</td>
        <td>${escapeHtml(item.default_price)}</td>
        <td>${escapeHtml(item.description || "")}</td>
      `;

      tbody.appendChild(tr);
    }

    return data;
  } catch (err) {
    showError(
      "讀取消費項目失敗",
      err,
    );

    return [];
  }
}

async function createCatalogItem() {
  try {
    const payload = {
      name: document
        .getElementById("catalog_item_name")
        .value
        .trim(),

      default_price: Number(
        document
          .getElementById("catalog_item_price")
          .value || 0,
      ),

      description:
        document
          .getElementById(
            "catalog_item_description",
          )
          .value
          .trim() || null,
    };

    const data = await api(
      "/items",
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
    );

    await showSuccess(
      "消費項目新增成功",
      `${data.name} / ID ${data.id}`,
    );

    document.getElementById(
      "catalog_item_name",
    ).value = "";

    document.getElementById(
      "catalog_item_price",
    ).value = "0";

    document.getElementById(
      "catalog_item_description",
    ).value = "";

    await loadCatalogItems();
  } catch (err) {
    showError(
      "消費項目新增失敗",
      err,
    );
  }
}

async function loadCatalogOptions() {
  const select =
    document.getElementById(
      "catalog_item_id",
    );

  if (!select) return;

  try {
    const data = await api("/items");

    select.innerHTML =
      '<option value="">請選擇消費項目</option>';

    if (data.length === 0) {
      const option =
        document.createElement("option");

      option.value = "";
      option.textContent =
        "尚未建立消費項目";
      option.disabled = true;

      select.appendChild(option);

      return;
    }

    for (const item of data) {
      const option =
        document.createElement("option");

      option.value = item.id;

      option.textContent =
        `${item.name}（預設價格 ${item.default_price}）`;

      option.dataset.name = item.name;
      option.dataset.price =
        item.default_price;

      select.appendChild(option);
    }
  } catch (err) {
    showError(
      "讀取消費項目失敗",
      err,
    );
  }
}

function applyCatalogItemPrice() {
  const select =
    document.getElementById(
      "catalog_item_id",
    );

  const selectedItem =
    select?.selectedOptions[0];

  const priceInput =
    document.getElementById("unit_price");

  if (!priceInput) return;

  priceInput.value =
    selectedItem?.dataset.price ?? "0";
}

async function initItemsPage() {
  if (await checkLoginStatus(true)) {
    await loadCatalogItems();
  }
}

async function initTransactionsPage() {
  if (await checkLoginStatus(true)) {
    await loadCatalogOptions();
  }
}

async function listUsers() {
  const tbody =
    document.getElementById("users-table");

  if (!tbody) return;

  tbody.innerHTML = "";

  try {
    const data = await api("/users");

    for (const user of data) {
      const tr =
        document.createElement("tr");

      tr.innerHTML = `
        <td>${user.id}</td>
        <td>${escapeHtml(user.username)}</td>
        <td>${escapeHtml(user.full_name || "")}</td>
        <td>${escapeHtml(user.role)}</td>
        <td>${user.is_active ? "是" : "否"}</td>
      `;

      tbody.appendChild(tr);
    }
  } catch (err) {
    showError(
      "讀取人員失敗",
      err,
    );
  }
}

async function createUser() {
  try {
    const payload = {
      username:
        document.getElementById(
          "new_username",
        ).value,

      password:
        document.getElementById(
          "new_password",
        ).value,

      full_name:
        document.getElementById(
          "new_full_name",
        ).value || null,

      role:
        document.getElementById(
          "new_role",
        ).value,

      is_active: true,
    };

    const data = await api(
      "/users",
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
    );

    await showSuccess(
      "新增帳號成功",
      data.username,
    );

    await listUsers();
  } catch (err) {
    showError(
      "新增帳號失敗",
      err,
    );
  }
}

async function loadMe() {
  const el =
    document.getElementById("me-result");

  if (!el) return;

  try {
    const data = await api("/users/me");

    el.textContent =
      JSON.stringify(data, null, 2);
  } catch (err) {
    el.textContent = err.message;
  }
}

function escapeHtml(value) {
  return String(value).replace(
    /[&<>'"]/g,
    (character) => (
      {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        "'": "&#039;",
        '"': "&quot;",
      }[character]
    ),
  );
}

async function changeMyPassword() {
  const oldPassword =
    document.getElementById(
      "old_password",
    ).value;

  const newPassword =
    document.getElementById(
      "new_password",
    ).value;

  const confirmPassword =
    document.getElementById(
      "confirm_password",
    ).value;

  if (
    !oldPassword ||
    !newPassword ||
    !confirmPassword
  ) {
    showError(
      "欄位未完成",
      "請完整輸入所有密碼欄位",
    );

    return;
  }

  if (newPassword !== confirmPassword) {
    showError(
      "密碼不一致",
      "新密碼與確認新密碼不一致",
    );

    return;
  }

  try {
    await api(
      "/users/me/password",
      {
        method: "PUT",
        body: JSON.stringify({
          old_password: oldPassword,
          new_password: newPassword,
        }),
      },
    );

    await showSuccess(
      "密碼修改成功，請重新登入",
    );

    localStorage.removeItem(
      "access_token",
    );

    setTimeout(() => {
      goToPage("/login");
    }, 800);
  } catch (err) {
    showError(
      "密碼修改失敗",
      err,
    );
  }
}

function updateAuthButton(isLogin) {
  const btn =
    document.getElementById("auth-btn");

  if (!btn) return;

  if (isLogin) {
    btn.textContent = "登出";
  } else {
    btn.textContent = "登入";
  }
}

function handleAuthButton() {
  const token =
    localStorage.getItem("access_token");

  if (token) {
    logout();
  } else {
    goToPage("/login");
  }
}

// ==================== 新增 CSV 功能 ====================

async function exportCustomersCsv() {
  const token =
    localStorage.getItem("access_token");

  if (!token) {
    Swal.fire(
      "請先登入",
      "",
      "warning",
    );

    return;
  }

  const res = await fetch(
    "/api/customers/export/csv",
    {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    },
  );

  if (!res.ok) {
    Swal.fire(
      "匯出失敗",
      "請確認權限或重新登入",
      "error",
    );

    return;
  }

  const blob = await res.blob();
  const url =
    window.URL.createObjectURL(blob);

  const link =
    document.createElement("a");

  link.href = url;
  link.download = "customers.csv";

  document.body.appendChild(link);
  link.click();

  link.remove();

  window.URL.revokeObjectURL(url);
}

// ==================== 頁面跳轉控制 ====================

let isNavigating = false;

function goToPage(
  url,
  title = "頁面載入中...",
) {
  if (isNavigating) return;

  isNavigating = true;

  showLoading(title);

  setTimeout(() => {
    sessionStorage.setItem(
      "page_navigation_loading",
      "true",
    );

    window.location.assign(url);
  }, 400);
}

document.addEventListener(
  "click",
  function (event) {
    const link =
      event.target.closest("a[href]");

    if (!link) return;

    if (
      event.defaultPrevented ||
      event.button !== 0 ||
      event.ctrlKey ||
      event.metaKey ||
      event.shiftKey ||
      event.altKey ||
      link.target === "_blank" ||
      link.hasAttribute("download")
    ) {
      return;
    }

    const url = new URL(
      link.href,
      window.location.href,
    );

    if (
      url.origin !==
      window.location.origin
    ) {
      return;
    }

    if (
      url.pathname ===
        window.location.pathname &&
      url.search ===
        window.location.search &&
      url.hash
    ) {
      return;
    }

    event.preventDefault();
    goToPage(url.href);
  },
);

// ================== 頁面跳轉控制結束 ==================