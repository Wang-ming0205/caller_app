// new version
const API_PREFIX = "/api";
let currentUser = null;
let apiLoadingCount = 0;
let apiLoadingCloseTimer = null;
let isInitialPageLoad =
  sessionStorage.getItem("page_navigation_loading") === "true";

function beginApiLoading() {
  if (apiLoadingCloseTimer) {
    clearTimeout(apiLoadingCloseTimer);
    apiLoadingCloseTimer = null;
  }

  apiLoadingCount += 1;
  showLoading(
    isInitialPageLoad
      ? "頁面載入中..."
      : "讀取中...",
  );
}

function endApiLoading() {
  apiLoadingCount = Math.max(0, apiLoadingCount - 1);

  if (apiLoadingCount > 0) return;

  // 延到下一輪再關閉，讓連續 await 的初始化 API 共用同一個動畫。
  apiLoadingCloseTimer = setTimeout(() => {
    if (apiLoadingCount > 0) return;

    hideLoading();
    apiLoadingCloseTimer = null;

    if (isInitialPageLoad) {
      isInitialPageLoad = false;
      sessionStorage.removeItem("page_navigation_loading");
    }
  }, 0);
}

async function api(path, options = {}) {
  const shouldShowLoading = options.showLoading !== false;

  if (shouldShowLoading) {
    beginApiLoading();
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
      endApiLoading();
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

function finishApiLoadingBeforeMessage() {
  if (apiLoadingCloseTimer) {
    clearTimeout(apiLoadingCloseTimer);
    apiLoadingCloseTimer = null;
  }

  apiLoadingCount = 0;
  hideLoading();

  if (isInitialPageLoad) {
    isInitialPageLoad = false;
    sessionStorage.removeItem("page_navigation_loading");
  }
}

async function showSuccess(title, text = "") {
  finishApiLoadingBeforeMessage();

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
  finishApiLoadingBeforeMessage();

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
  finishApiLoadingBeforeMessage();

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
  finishApiLoadingBeforeMessage();

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
          id="birthday-${customer.id}"
          type="date"
          value="${escapeHtml(customer.birthday || "")}"
        >
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
        
      birthday:document
        .getElementById(`birthday-${id}`)
        .value || null,

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

// async function customerSummary(id) {
//   const el =
//     document.getElementById("summary-result");

//   if (!el) return;

//   try {
//     const data = await api(
//       `/customers/${id}/summary`,
//     );

//     el.textContent =
//       JSON.stringify(data, null, 2);
//   } catch (err) {
//     el.textContent = err.message;
//   }
// }

function formatSummaryDate(value) {
  if (!value) return "日期不明";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return String(value);
  }

  return date.toLocaleString("zh-TW", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}


function renderCustomerSummary(
  summary,
  target,
) {
  const container =
    typeof target === "string"
      ? document.getElementById(target)
      : target;

  if (!container) return;

  const transactions =
    summary.recent_transactions || [];

  const historyHtml =
    transactions.length === 0
      ? `
        <div class="customer-summary-empty">
          這位客戶目前沒有消費紀錄。
        </div>
      `
      : transactions.map((transaction) => {
          const items =
            transaction.items || [];

          const itemsHtml =
            items.length === 0
              ? `
                <p class="hint">
                  此筆消費沒有項目明細。
                </p>
              `
              : `
                <table>
                  <thead>
                    <tr>
                      <th>項目</th>
                      <th>數量</th>
                      <th>單價</th>
                      <th>小計</th>
                    </tr>
                  </thead>

                  <tbody>
                    ${items.map((item) => `
                      <tr>
                        <td>
                          ${escapeHtml(item.item_name)}
                        </td>

                        <td>
                          ${Number(item.qty) || 0}
                        </td>

                        <td>
                          ${formatMoney(item.unit_price)}
                        </td>

                        <td>
                          ${formatMoney(item.subtotal)}
                        </td>
                      </tr>
                    `).join("")}
                  </tbody>
                </table>
              `;

          const noteHtml = transaction.note
            ? `
              <p class="customer-history-note">
                備註：
                ${escapeHtml(transaction.note)}
              </p>
            `
            : "";

          return `
            <details class="customer-history-entry">
              <summary>
                <strong>
                  第 ${transaction.visit_number} 次消費
                </strong>

                <span>
                  ${formatSummaryDate(
                    transaction.record_date,
                  )}
                </span>

                <strong>
                  ${formatMoney(
                    transaction.total_amount,
                  )}
                </strong>
              </summary>

              <div class="customer-history-detail">
                ${itemsHtml}
                ${noteHtml}
              </div>
            </details>
          `;
        }).join("");

  container.innerHTML = `
    <section class="customer-summary-header">
      <h3>
        ${escapeHtml(summary.name)}
      </h3>

      <p>
        ID ${summary.customer_id}
        ／
        ${escapeHtml(summary.phone_number)}
      </p>

      <p>
        生日：
        ${
          summary.birthday
            ? escapeHtml(summary.birthday)
            : "未填寫"
        }
      </p>
    </section>

    <section class="customer-summary-stats">
      <div class="customer-summary-stat">
        <span>總消費次數</span>

        <strong>
          ${Number(summary.transaction_count) || 0} 次
        </strong>
      </div>

      <div class="customer-summary-stat">
        <span>總消費金額</span>

        <strong>
          ${formatMoney(summary.total_amount)}
        </strong>
      </div>
    </section>

    <section>
      <h3>最近五筆消費</h3>

      <div class="customer-history-list">
        ${historyHtml}
      </div>
    </section>
  `;

  container.classList.remove("hidden");
}


// async function customerSummary(id) {
//   const container =
//     document.getElementById("summary-result");

//   if (!container) return;

//   try {
//     const summary = await api(
//       `/customers/${id}/summary`,
//     );

//     renderCustomerSummary(
//       summary,
//       container,
//     );

//     container.scrollIntoView({
//       behavior: "smooth",
//       block: "start",
//     });
//   } catch (err) {
//     showError("讀取會員摘要失敗", err);
//   }
// }
function formatSummaryDate(value) {
  if (!value) return "日期不明";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return String(value);
  }

  return date.toLocaleString("zh-TW", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}


function renderCustomerSummary(
  summary,
  target,
) {
  const container =
    typeof target === "string"
      ? document.getElementById(target)
      : target;

  if (!container) return;

  const transactions =
    summary.recent_transactions || [];

  const historyHtml =
    transactions.length === 0
      ? `
        <div class="customer-summary-empty">
          這位客戶目前沒有消費紀錄。
        </div>
      `
      : transactions
          .map((transaction) => {
            const items =
              transaction.items || [];

            const itemsHtml =
              items.length === 0
                ? `
                  <p class="hint">
                    此筆消費沒有項目明細。
                  </p>
                `
                : `
                  <table>
                    <thead>
                      <tr>
                        <th>項目</th>
                        <th>數量</th>
                        <th>單價</th>
                        <th>小計</th>
                      </tr>
                    </thead>

                    <tbody>
                      ${items
                        .map((item) => `
                          <tr>
                            <td>
                              ${escapeHtml(
                                item.item_name,
                              )}
                            </td>

                            <td>
                              ${Number(item.qty) || 0}
                            </td>

                            <td>
                              ${formatMoney(
                                item.unit_price,
                              )}
                            </td>

                            <td>
                              ${formatMoney(
                                item.subtotal,
                              )}
                            </td>
                          </tr>
                        `)
                        .join("")}
                    </tbody>
                  </table>
                `;

            const noteHtml =
              transaction.note
                ? `
                  <p class="customer-history-note">
                    備註：
                    ${escapeHtml(transaction.note)}
                  </p>
                `
                : "";

            return `
              <details class="customer-history-entry">
                <summary>
                  <strong>
                    <span class="history-arrow">
                      ▶
                    </span>

                    第 ${
                      Number(
                        transaction.visit_number,
                      ) || 0
                    } 次消費
                  </strong>

                  <span>
                    ${formatSummaryDate(
                      transaction.record_date,
                    )}
                  </span>

                  <strong>
                    ${formatMoney(
                      transaction.total_amount,
                    )}
                  </strong>
                </summary>

                <div class="customer-history-detail">
                  ${itemsHtml}
                  ${noteHtml}
                </div>
              </details>
            `;
          })
          .join("");

  container.innerHTML = `
    <section class="customer-summary-header">
      <h3>
        ${escapeHtml(summary.name)}
      </h3>

      <p>
        ID ${Number(summary.customer_id)}
        ／
        ${escapeHtml(summary.phone_number)}
      </p>
    </section>

    <section class="customer-summary-stats">
      <div class="customer-summary-stat">
        <span>總消費次數</span>

        <strong>
          ${
            Number(summary.transaction_count) || 0
          } 次
        </strong>
      </div>

      <div class="customer-summary-stat">
        <span>總消費金額</span>

        <strong>
          ${formatMoney(summary.total_amount)}
        </strong>
      </div>
    </section>

    <section>
      <h3>最近五筆消費</h3>

      <div class="customer-history-list">
        ${historyHtml}
      </div>
    </section>
  `;

  container.classList.remove("hidden");
}


async function customerSummary(id) {
  const container =
    document.getElementById("summary-result");

  if (!container) return;

  try {
    const summary = await api(
      `/customers/${id}/summary`,
    );

    renderCustomerSummary(
      summary,
      container,
    );

    container.scrollIntoView({
      behavior: "smooth",
      block: "start",
    });
  } catch (err) {
    showError(
      "讀取會員摘要失敗",
      err,
    );
  }
}

function clearCustomerForm() {
  document.getElementById("name").value = "";
  document.getElementById("phone_number").value = "";
  document.getElementById("gender").value = "";
  document.getElementById("birthday").value = "";
  document.getElementById("note").value = "";
}


let catalogItems = [];
let isCreatingTransaction = false;

let transactionItems = [];
let selectedTransactionCustomer = null;
let customerHistoryTotal = 0;
let transactionCustomerSearchResults = [];

let selectedServiceCategory = null;
let selectedService = null;
let selectedServiceVariant = null;

const SERVICE_CATALOG = {
  "剪": [
    {
      name: "剪髮",
      startingPrice: 0,
    },
  ],

  "洗": [
    {
      name: "健康洗",
      price: 300,
    },
    {
      name: "護色洗",
      price: 400,
    },
    {
      name: "SPA 輕鬆洗",
      startingPrice: 0,
    },
    {
      name: "SPA 木梳按摩療程",
      price: 450,
    },
  ],

  "染": [
    {
      name: "染髮",
      prices: {
        "極短": 1999,
        "短": 2499,
        "中": 2999,
        "長": 3499,
        "過腰": 3999,
      },
      priceSuffix: "起",
    },
    {
      name: "沐浴染",
      startingPrice: 800,
    },
    {
      name: "去色",
      startingPrice: 1000,
    },
    {
      name: "補染（不含洗）",
      startingPrice: 1200,
    },
  ],

  "燙": [
    {
      name: "冷塑美型燙",
      prices: {
        "極短": 2000,
        "短": 2300,
        "中": 2600,
        "長": 2900,
        "過腰": 3200,
      },
      priceSuffix: "起",
    },
    {
      name: "溫塑美型燙",
      prices: {
        "極短": 2200,
        "短": 2600,
        "中": 3000,
        "長": 3400,
        "過腰": 4000,
      },
      priceSuffix: "起",
    },
    {
      name: "自然捲矯正加價購",
      prices: {
        "輕微": 500,
        "嚴重": 1000,
      },
    },
    {
      name: "髮根（不含洗）",
      startingPrice: 1500,
    },
    {
      name: "瀏海（不含洗）",
      price: 250,
    },
  ],

  "護髮": [
    {
      name: "精蛋白系統",
      prices: {
        "短": 800,
        "中": 1000,
        "長": 1200,
        "過腰": 1600,
      },
      priceSuffix: "起",
    },
    {
      name: "三劍客",
      prices: {
        "短": 650,
        "中": 900,
        "長": 1100,
        "過腰": 1500,
      },
      priceSuffix: "起",
    },
  ],

  "頭皮": [
    {
      name: "角質淨化療程",
      price: 499,
    },
    {
      name: "深層清潔療程",
      price: 799,
    },
    {
      name: "死海礦泥療程",
      price: 999,
    },
    {
      name: "夏日海洋療程",
      price: 999,
    },
    {
      name: "精油按摩療程",
      price: 1200,
    },
  ],

  "臉部": [
    {
      name: "臉部深層淨化療程",
      price: 400,
    },
  ],

  "其他": [
    {
      name: "其他項目",
      startingPrice: 0,
      allowCustomName: true,
    },
  ],
};

function formatMoney(value) {
  const amount = Number(value) || 0;

  return `NT$ ${amount.toLocaleString("zh-TW")}`;
}

function clearSelectedCategory() {
  selectedServiceCategory = null;
  selectedService = null;
  selectedServiceVariant = null;

  document
    .querySelectorAll("[data-category]")
    .forEach((button) => {
      button.classList.remove("selected");
    });

  const serviceButtons =
    document.getElementById("service-buttons");

  const lengthButtons =
    document.getElementById("length-buttons");

  const servicePanel =
    document.getElementById(
      "service-selection-panel",
    );

  const lengthPanel =
    document.getElementById(
      "length-selection-panel",
    );

  const summary =
    document.getElementById(
      "selected-service-summary",
    );

  const itemName =
    document.getElementById("item_name");

  const itemDescription =
    document.getElementById(
      "item_description",
    );

  if (serviceButtons) {
    serviceButtons.innerHTML = "";
  }

  if (lengthButtons) {
    lengthButtons.innerHTML = "";
  }

  if (servicePanel) {
    servicePanel.classList.add("hidden");
  }

  if (lengthPanel) {
    lengthPanel.classList.add("hidden");
  }

  if (summary) {
    summary.textContent = "";
    summary.classList.add("hidden");
  }

  if (itemName) {
    itemName.value = "";
    itemName.readOnly = true;
  }

  if (itemDescription) {
    itemDescription.value = "";
  }
}

// function clearVerifiedTransactionCustomer() {
//   const customerId =
//     document.getElementById("customer_id");

//   const selectedResult  = document.getElementById(
//     "transaction-customer-result",
//   );

//  const searchResults = document.getElementById(
//     "transaction-customer-results",
//   );


// if (customerId) {
//     customerId.value = "";
//   }

//   if (selectedResult) {
//     selectedResult.textContent = "";
//     selectedResult.classList.add("hidden");
//   }

//   if (searchResults) {
//     searchResults.innerHTML = "";
//     searchResults.classList.add("hidden");
//   }

//   transactionCustomerSearchResults = [];
//   selectedTransactionCustomer = null;
//   customerHistoryTotal = 0;
//   transactionItems = [];

//   clearSelectedCategory();
//   renderTransactionItems();
// }
function clearVerifiedTransactionCustomer() {
  const customerId =
    document.getElementById("customer_id");

  const selectedResult =
    document.getElementById(
      "transaction-customer-result",
    );

  const searchResults =
    document.getElementById(
      "transaction-customer-results",
    );

  const customerSummary =
    document.getElementById(
      "transaction-customer-summary",
    );

  if (customerId) {
    customerId.value = "";
  }

  if (selectedResult) {
    selectedResult.textContent = "";
    selectedResult.classList.add("hidden");
  }

  if (searchResults) {
    searchResults.innerHTML = "";
    searchResults.classList.add("hidden");
  }

  if (customerSummary) {
    customerSummary.innerHTML = "";
    customerSummary.classList.add("hidden");
  }

  transactionCustomerSearchResults = [];
  selectedTransactionCustomer = null;
  customerHistoryTotal = 0;
  transactionItems = [];

  clearSelectedCategory();
  renderTransactionItems();
}

// function showVerifiedTransactionCustomer(
//   customer,
//   summary,
// ) {
//   const customerId =
//     document.getElementById("customer_id");

//   const result = document.getElementById(
//     "transaction-customer-result",
//   );

//   selectedTransactionCustomer = customer;

//   customerHistoryTotal =
//     Number(summary?.total_amount) || 0;

//   if (customerId) {
//     customerId.value = customer.id;
//   }

//   if (result) {
//     result.textContent =
//       `已選客戶：ID ${customer.id}／` +
//       `${customer.name}／` +
//       `${customer.phone_number}`;

//     result.classList.remove(
//       "hidden",
//       "error",
//     );
//   }

//   renderTransactionItems();
// }
function showVerifiedTransactionCustomer(
  customer,
  summary,
) {
  const customerId =
    document.getElementById("customer_id");

  const result =
    document.getElementById(
      "transaction-customer-result",
    );

  selectedTransactionCustomer = customer;

  customerHistoryTotal =
    Number(summary?.total_amount) || 0;

  if (customerId) {
    customerId.value = customer.id;
  }

  if (result) {
    result.textContent =
      `已選客戶：ID ${customer.id}／` +
      `${customer.name}／` +
      `${customer.phone_number}`;

    result.classList.remove(
      "hidden",
      "error",
    );
  }

  renderCustomerSummary(
    summary,
    "transaction-customer-summary",
  );

  renderTransactionItems();
}

function renderTransactionCustomerResults(
  customers,
) {
  const container = document.getElementById(
    "transaction-customer-results",
  );

  if (!container) return;

  container.innerHTML = "";

  if (customers.length === 0) {
    container.classList.add("hidden");
    return;
  }

  for (const customer of customers) {
    const button = document.createElement("button");

    button.type = "button";
    button.className =
      "transaction-customer-result-button";

    button.innerHTML = `
      <strong>ID ${customer.id}</strong>
      ${escapeHtml(customer.name)}
      ／
      ${escapeHtml(customer.phone_number)}
    `;

    button.addEventListener("click", () => {
      selectTransactionCustomer(customer.id);
    });

    container.appendChild(button);
  }

  container.classList.remove("hidden");
}


async function selectTransactionCustomer(
  customerId,
) {
  const customer =
    transactionCustomerSearchResults.find(
      item =>
        Number(item.id) === Number(customerId),
    );

  if (!customer) {
    showError(
      "選擇失敗",
      "找不到選擇的客戶資料",
    );

    return;
  }

  try {
    const summary = await api(
      `/customers/${customer.id}/summary`,
    );

    showVerifiedTransactionCustomer(
      customer,
      summary,
    );

    const container = document.getElementById(
      "transaction-customer-results",
    );

    if (container) {
      container.innerHTML = "";
      container.classList.add("hidden");
    }
  } catch (err) {
    clearVerifiedTransactionCustomer();

    showError(
      "讀取客戶資料失敗",
      err,
    );
  }
}

async function findTransactionCustomer() {
  const queryInput = document.getElementById(
    "tx_phone_number",
  );
  const keyword = queryInput.value.trim();

  if (!keyword) {
    clearVerifiedTransactionCustomer();

    showError(
      "欄位未完成",
      "請輸入客戶 ID、姓名或手機末碼",
    );

    return [];
  }

  clearVerifiedTransactionCustomer();

  try {
    const customers = await api(
      `/customers/search/list?q=${
        encodeURIComponent(keyword)
      }`,
    );

    transactionCustomerSearchResults = customers;

    if (customers.length === 0) {
      showError(
        "找不到客戶",
        "沒有符合搜尋條件的客戶",
      );

      return [];
    }

    renderTransactionCustomerResults(customers);

    return customers;
  } catch (err) {
    clearVerifiedTransactionCustomer();

    showError(
      "查詢客戶失敗",
      err,
    );

    return [];
  }
}

function selectServiceCategory(
  category,
  selectedButton,
) {
  selectedServiceCategory = category;
  selectedService = null;
  selectedServiceVariant = null;

  document
    .querySelectorAll("[data-category]")
    .forEach((button) => {
      button.classList.remove("selected");
    });

  selectedButton.classList.add("selected");

  const itemName =
    document.getElementById("item_name");

  const unitPrice =
    document.getElementById("unit_price");

  const lengthPanel =
    document.getElementById(
      "length-selection-panel",
    );

  const lengthButtons =
    document.getElementById("length-buttons");

  const summary =
    document.getElementById(
      "selected-service-summary",
    );

  itemName.value = "";
  itemName.readOnly = true;
  unitPrice.value = "0";

  lengthPanel.classList.add("hidden");
  lengthButtons.innerHTML = "";

  summary.textContent = "";
  summary.classList.add("hidden");

  renderServiceButtons(category);
}

function renderServiceButtons(category) {
  const panel =
    document.getElementById(
      "service-selection-panel",
    );

  const container =
    document.getElementById("service-buttons");

  const services =
    SERVICE_CATALOG[category] || [];

  container.innerHTML = "";

  services.forEach((service, index) => {
    const button = document.createElement("button");

    button.type = "button";
    button.dataset.serviceIndex = String(index);
    button.textContent =
      getServiceButtonText(service);

    button.addEventListener("click", () => {
      selectService(service, button);
    });

    container.appendChild(button);
  });

  panel.classList.remove("hidden");
}

function getServiceButtonText(service) {
  if (service.prices) {
    const prices = Object.values(service.prices);
    const minimumPrice = Math.min(...prices);

    return `${service.name}／${formatMoney(
      minimumPrice,
    )}${service.priceSuffix || ""}`;
  }

  if (service.startingPrice !== undefined) {
    return `${service.name}／${formatMoney(
      service.startingPrice,
    )} 起`;
  }

  return `${service.name}／${formatMoney(
    service.price,
  )}`;
}

function selectService(service, selectedButton) {
  selectedService = service;
  selectedServiceVariant = null;

  document
    .querySelectorAll("[data-service-index]")
    .forEach((button) => {
      button.classList.remove("selected");
    });

  selectedButton.classList.add("selected");

  const itemName =
    document.getElementById("item_name");

  const unitPrice =
    document.getElementById("unit_price");

  const lengthPanel =
    document.getElementById(
      "length-selection-panel",
    );

  const lengthButtons =
    document.getElementById("length-buttons");

  itemName.value = service.name;
  itemName.readOnly = !service.allowCustomName;

  lengthButtons.innerHTML = "";

  if (service.prices) {
    unitPrice.value = "0";

    renderServiceVariants(service);
    lengthPanel.classList.remove("hidden");

    updateSelectedServiceSummary();
    return;
  }

  lengthPanel.classList.add("hidden");

  if (service.startingPrice !== undefined) {
    unitPrice.value = service.startingPrice;
  } else {
    unitPrice.value = service.price;
  }

  updateSelectedServiceSummary();
}

function renderServiceVariants(service) {
  const container =
    document.getElementById("length-buttons");

  container.innerHTML = "";

  Object.entries(service.prices).forEach(
    ([variant, price]) => {
      const button =
        document.createElement("button");

      button.type = "button";
      button.dataset.serviceVariant = variant;
      button.textContent =
        `${variant}／${formatMoney(price)}`;

      button.addEventListener("click", () => {
        selectServiceVariant(
          variant,
          price,
          button,
        );
      });

      container.appendChild(button);
    },
  );
}

function selectServiceVariant(
  variant,
  price,
  selectedButton,
) {
  selectedServiceVariant = variant;

  document
    .querySelectorAll("[data-service-variant]")
    .forEach((button) => {
      button.classList.remove("selected");
    });

  selectedButton.classList.add("selected");

  document.getElementById(
    "item_name",
  ).value = `${selectedService.name}－${variant}`;

  document.getElementById(
    "unit_price",
  ).value = price;

  updateSelectedServiceSummary();
}

function updateSelectedServiceSummary() {
  const summary =
    document.getElementById(
      "selected-service-summary",
    );

  if (!selectedService) {
    summary.textContent = "";
    summary.classList.add("hidden");
    return;
  }

  let text =
    `已選擇：${selectedServiceCategory}／` +
    selectedService.name;

  if (selectedServiceVariant) {
    text += `／${selectedServiceVariant}`;
  }

  const unitPrice = Number(
    document.getElementById("unit_price").value,
  );

  if (Number.isFinite(unitPrice)) {
    text += `／${formatMoney(unitPrice)}`;
  }

  summary.textContent = text;
  summary.classList.remove("hidden");
}

function addTransactionItem() {
  let itemName = document
    .getElementById("item_name")
    .value
    .trim();

  const itemDescription = document
    .getElementById("item_description")
    .value
    .trim();

  const qty = Number(
    document.getElementById("qty").value,
  );

  const unitPrice = Number(
    document.getElementById("unit_price").value,
  );

  if (!selectedServiceCategory) {
    showError(
      "尚未選擇分類",
      "請先選擇服務分類",
    );

    return;
  }

  if (!selectedService) {
    showError(
      "尚未選擇服務",
      "請選擇本次消費的服務項目",
    );

    return;
  }

  if (
    selectedService.prices &&
    !selectedServiceVariant
  ) {
    showError(
      "尚未選擇規格",
      "請選擇髮長或服務規格",
    );

    return;
  }

  if (!itemName) {
    showError(
      "項目名稱錯誤",
      "請輸入或選擇消費項目",
    );

    return;
  }

  if (!Number.isInteger(qty) || qty < 1) {
    showError(
      "數量錯誤",
      "數量至少必須是 1",
    );

    return;
  }

  if (
    !Number.isFinite(unitPrice) ||
    unitPrice < 0
  ) {
    showError(
      "價格錯誤",
      "價格不可小於 0",
    );

    return;
  }

  if (
    selectedServiceCategory !== "其他" &&
    unitPrice === 0
  ) {
    showError(
      "價格未填寫",
      "請輸入本次服務的實際價格",
    );

    return;
  }

  if (itemDescription) {
    itemName += `（${itemDescription}）`;
  }

  transactionItems.push({
    item_name: itemName,
    qty,
    unit_price: unitPrice,
  });

  document.getElementById("qty").value = "1";
  document.getElementById(
    "unit_price",
  ).value = "0";

  clearSelectedCategory();
  renderTransactionItems();
}

function removeTransactionItem(index) {
  transactionItems.splice(index, 1);
  renderTransactionItems();
}

function calculateCurrentSpending() {
  return transactionItems.reduce(
    (total, item) => (
      total +
      Number(item.qty) *
      Number(item.unit_price)
    ),
    0,
  );
}

function renderTransactionItems() {
  const tbody = document.getElementById(
    "current-items-table",
  );

  const currentSpending =
    document.getElementById(
      "current-spending",
    );

  const totalSpending =
    document.getElementById(
      "total-spending",
    );

  const currentTotal =
    calculateCurrentSpending();

  if (currentSpending) {
    currentSpending.textContent =
      formatMoney(currentTotal);
  }

  if (totalSpending) {
    totalSpending.textContent =
      formatMoney(
        customerHistoryTotal + currentTotal,
      );
  }

  if (!tbody) return;

  tbody.innerHTML = "";

  if (transactionItems.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="4">
          尚未加入消費項目
        </td>
      </tr>
    `;

    return;
  }

  transactionItems.forEach((item, index) => {
    const subtotal =
      Number(item.qty) *
      Number(item.unit_price);

    const row = document.createElement("tr");

    row.innerHTML = `
      <td>${escapeHtml(item.item_name)}</td>
      <td>${item.qty}</td>
      <td>${formatMoney(subtotal)}</td>
      <td>
        <button
          type="button"
          onclick="removeTransactionItem(${index})"
        >
          移除
        </button>
      </td>
    `;

    tbody.appendChild(row);
  });
}

async function createTransaction() {
  if (isCreatingTransaction) return;

  const selectedCustomerId = Number(
    document.getElementById("customer_id").value,
  );

  if (
    !selectedCustomerId ||
    !selectedTransactionCustomer ||
    selectedCustomerId !== Number(selectedTransactionCustomer.id)
  ) {
    showError(
      "尚未確認客戶",
      "請先使用手機號碼查詢客戶",
    );

    return;
  }

  if (transactionItems.length === 0) {
    showError(
      "沒有消費項目",
      "請至少加入一個消費項目",
    );

    return;
  }

  isCreatingTransaction = true;

  try {
    const payload = {
      customer_id:
        selectedTransactionCustomer.id,

      note:
        document
          .getElementById("tx_note")
          .value
          .trim() || null,

      items: transactionItems.map((item) => ({
        item_name: item.item_name,
        qty: item.qty,
        unit_price: item.unit_price,
      })),
    };

    const data = await api(
      "/transactions",
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
    );

    customerHistoryTotal +=
      Number(data.total_amount) || 0;

    try {
        const updatedSummary = await api(
          `/customers/${
            selectedTransactionCustomer.id
          }/summary`,
        );

        customerHistoryTotal =
          Number(updatedSummary.total_amount) || 0;

        renderCustomerSummary(
          updatedSummary,
          "transaction-customer-summary",
        );
    } catch (summaryError) {
      console.error(
        "消費已新增，但摘要更新失敗：",
        summaryError,
      );
    }

    transactionItems = [];

    document.getElementById(
      "tx_note",
    ).value = "";

    clearSelectedCategory();
    renderTransactionItems();

    await showSuccess(
      "消費新增成功",
      `此次消費 ${formatMoney(
        data.total_amount,
      )}`,
    );
  } catch (err) {
    showError(
      "新增消費失敗",
      err,
    );
  } finally {
    isCreatingTransaction = false;
  }
}

async function deleteCatalogItem(id) {
  const ok = await confirmAction(
    "確定刪除此消費項目？",
  );

  if (!ok) return;

  try {
    await api(`/items/${id}`, {
      method: "DELETE",
    });

    await showSuccess("消費項目刪除成功");
    await refreshCatalogItems();
  } catch (err) {
    showError("刪除消費項目失敗", err);
  }
}

async function loadCatalogOptions() {
  const datalist = document.getElementById(
    "catalog-item-suggestions",
  );

  if (!datalist) return [];

  try {
    const data = await api("/items");
    catalogItems = data;
    datalist.innerHTML = "";

    for (const item of data) {
      const option =
        document.createElement("option");

      option.value = item.name;
      option.label =
        `${item.name}（${item.default_price}）`;
      datalist.appendChild(option);
    }

    return data;
  } catch (err) {
    showError(
      "讀取消費項目失敗",
      err,
    );
  }
}

function applyCatalogItemPrice() {
  const name = document
    .getElementById("item_name")
    ?.value
    .trim();

  const matchedItem = catalogItems.find(
    (item) => item.name === name,
  );

  if (matchedItem) {
    document.getElementById(
      "unit_price",
    ).value = matchedItem.default_price;
  }
}

async function refreshCatalogItems() {
  await Promise.all([
    loadCatalogItems(),
    loadCatalogOptions(),
  ]);
}

async function initItemsPage() {
  if (await checkLoginStatus(true)) {
    await loadCatalogItems();
  }
}

async function initTransactionsPage() {
  const loggedIn =
    await checkLoginStatus(true);

  if (!loggedIn) return;

  transactionItems = [];
  selectedTransactionCustomer = null;
  customerHistoryTotal = 0;

  renderTransactionItems();
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
