// // new version
// const API_PREFIX = "/api";

// async function api(path, options = {}) {
//   // 如果剛從其他頁面透過 goToPage() 跳轉過來，
//   // 舊頁面已經顯示過「頁面載入中」，第一個初始化 API 就不要再顯示「讀取中」。
//   const skipInitialLoading =
//     options.showLoading !== false &&
//     sessionStorage.getItem("page_navigation_loading") === "true";

//   if (skipInitialLoading) {
//     // 只略過新頁面的第一個 API，之後的新增、查詢、刪除仍會顯示「讀取中」。
//     sessionStorage.removeItem("page_navigation_loading");
//   }

//   const shouldShowLoading = options.showLoading !== false && !skipInitialLoading;

//   if (shouldShowLoading) {
//     showLoading();
//   }

//   try {
//     const headers = {
//       "Content-Type": "application/json",
//       ...(options.headers || {}),
//     };

//     const currentToken = localStorage.getItem("access_token");

//     if (currentToken){
//       headers.Authorization = `Bearer ${currentToken}`;
//     }
  
//     const res = await fetch(`${API_PREFIX}${path}`, {
//       ...options,
//       headers,
//     });

//     const text = await res.text();

//     let data = null;
//     try {
//       data = text ? JSON.parse(text) : null;
//     } catch {
//       data = text;
//     }

//     if (!res.ok) {
//       const detail = data && data.detail ? data.detail : `HTTP ${res.status}`;
//       throw new Error(detail);
//     }

//     return data;
//   } finally {
//     if (shouldShowLoading) {
//       hideLoading();
//     }
//   }
// }

// function hasSwal() {
//   return typeof Swal !== "undefined";
// }

// function showLoading(title = "讀取中...") {
//   if (!hasSwal()) return;

//   Swal.fire({
//     title,
//     allowOutsideClick: false,
//     allowEscapeKey: false,
//     showConfirmButton: false,
//     didOpen: () => {
//       Swal.showLoading();
//     },
//   });
// }

// function hideLoading() {
//   if (!hasSwal()) return;
//   Swal.close();
// }

// async function showSuccess(title, text = "") {
//   if (hasSwal()) {
//     await Swal.fire({
//       icon: "success",
//       title,
//       text,
//       timer: 1200,
//       showConfirmButton: false,
//     });
//   } else {
//     window.alert(text ? `${title}：${text}` : title);
//   }
// }

// function showError(title, err) {
//   const text = err?.message || String(err);

//   if (hasSwal()) {
//     Swal.fire({
//       icon: "error",
//       title,
//       text,
//     });
//   } else {
//     window.alert(`${title}：${text}`);
//   }
// }

// function showInfo(title, text = "") {
//   if (hasSwal()) {
//     Swal.fire({
//       icon: "info",
//       title,
//       text,
//     });
//   } else {
//     window.alert(text ? `${title}：${text}` : title);
//   }
// }

// async function confirmAction(title, text = "此操作無法復原") {
//   if (hasSwal()) {
//     const result = await Swal.fire({
//       title,
//       text,
//       icon: "warning",
//       showCancelButton: true,
//       confirmButtonText: "確定",
//       cancelButtonText: "取消",
//     });

//     return result.isConfirmed;
//   }

//   return confirm(title);
// }

// //登入登出
// async function checkLoginStatus(redirectWhenMissing = true) {
//   const el = document.getElementById("login-status");
//   const currentToken = localStorage.getItem("access_token");

//   if (!currentToken) {
//     if (el) el.textContent = "尚未登入";
//     updateAuthButton(false);

//     if (redirectWhenMissing) {
//           goToPage("/login");
//     }

//     return false;
//   }

//   try {
//     const me = await api("/auth/me", { showLoading: false });

//     if (el) {
//       el.textContent = `已登入：${me.username}（${me.role}）`;
//     }

//     updateAuthButton(true);

//     return true;

//   } catch (err) {
//     localStorage.removeItem("access_token");

//     if (el) {
//       el.textContent = "登入已失效";
//     }

//     updateAuthButton(false);

//     if (redirectWhenMissing) {
//       window.location.href = "/login";
//     }

//     return false;
//   }
// }

// async function login() {
//   try {
//     const data = await api("/auth/login", {
//       method: "POST",
//       body: JSON.stringify({
//         username: document.getElementById("username").value,
//         password: document.getElementById("password").value,
//       }),
//     });
//     localStorage.setItem("access_token", data.access_token);
//     await showSuccess("登入成功");
//     goToPage("/");
//   } catch (err) {
//     showError("登入失敗", err);
//   }
// }

// function logout() {
//   localStorage.removeItem("access_token");
//   goToPage("/login");
// }

// async function seedData() {
//   try {
//     const data = await api("/setup/seed", {method: "POST"});
//     await showSuccess("測試資料建立完成", data.message || "");
//   } catch (err) {
//     showError("建立測試資料失敗", err);
//   }
// }

// async function checkHealth() {
//   const el = document.getElementById("health-result");
//   try {
//     const data = await fetch("/health").then(r => r.json());
//     el.textContent = JSON.stringify(data, null, 2);
//   } catch (err) {
//     el.textContent = err.message;
//   }
// }

// async function initHome() {
//   const ok = await checkLoginStatus(true);
//   if (ok) {
//     loadLatestCustomers();
//   }
// }

// let isCreatingCustomer = false;

// async function createCustomer() {
//   if (isCreatingCustomer) return;

//   isCreatingCustomer = true;


//   try {
//     const payload = {
//       name: document.getElementById("name").value.trim(),
//       phone_number: document.getElementById("phone_number").value.trim(),
//       gender: document.getElementById("gender").value || null,
//       birthday: document.getElementById("birthday").value || null,
//       note: document.getElementById("note").value || null,
//     };

//     const data = await api("/customers", {
//       method: "POST",
//       body: JSON.stringify(payload),
//     });

//     await showSuccess('新增成功',`${data.name} / ID ${data.id}`);
//     clearCustomerForm();
//     loadLatestCustomers();

//   } catch (err) {
//     showError("新增失敗",err);
//   }finally{
//     isCreatingCustomer = false;
//   }
// }

// async function loadLatestCustomers() {
//   const tbody = document.getElementById("customer-table");
//   if (!tbody) return;

//   try {
//     const data = await api("/customers/");
//     renderCustomerTable(data);
//   } catch (err) {
//     showError("讀取最新客戶失敗", err);
//   }
// }

// async function searchCustomers() {
//   const q = document.getElementById("q").value.trim();

//   if (!q) {
//     loadLatestCustomers();
//     return;
//   }

//   try {
//     const data = await api(`/customers/search/list?q=${encodeURIComponent(q)}`);
//     renderCustomerTable(data);
//   } catch (err) {
//     showError("查詢失敗", err);
//   }
// }

// function renderCustomerTable(customers) {
//   const tbody = document.getElementById("customer-table");
//   if (!tbody) return;

//   tbody.innerHTML = "";

//   for (const c of customers) {
//     const tr = document.createElement("tr");

//     tr.innerHTML = `
//       <td>${c.id}</td>
//       <td><input id="name-${c.id}" value="${escapeHtml(c.name)}"></td>
//       <td><input id="phone-${c.id}" value="${escapeHtml(c.phone_number)}"></td>
//       <td>
//         <select id="gender-${c.id}">
//           <option value="" ${!c.gender ? "selected" : ""}>未填</option>
//           <option value="男" ${c.gender === "男" ? "selected" : ""}>男</option>
//           <option value="女" ${c.gender === "女" ? "selected" : ""}>女</option>
//         </select>
//       </td>
//       <td><input id="note-${c.id}" value="${escapeHtml(c.note || "")}"></td>
//       <td>
//         <button onclick="updateCustomer(${c.id})">儲存</button>
//         <button onclick="customerSummary(${c.id})">摘要</button>
//         <button onclick="deleteCustomer(${c.id})">刪除</button>
//       </td>
//     `;

//     tbody.appendChild(tr);
//   }
// }

// async function updateCustomer(id) {
//   try {
//     const payload = {
//       name: document.getElementById(`name-${id}`).value.trim(),
//       phone_number: document.getElementById(`phone-${id}`).value.trim(),
//       gender: document.getElementById(`gender-${id}`).value || null,
//       note: document.getElementById(`note-${id}`).value || null,
//     };

//     const data = await api(`/customers/${id}`, {
//       method: "PUT",
//       body: JSON.stringify(payload),
//     });

//     await showSuccess("修改成功",data.name);
//     loadLatestCustomers();

//   } catch (err) {
//     showError("修改失敗", err);
//   }
// }

// async function deleteCustomer(id) {
//     const ok = await confirmAction("確定刪除？");
//     if (!ok) return;

//     try {
//       await api(`/customers/${id}`, {
//         method: "DELETE",
//       });

//       await showSuccess("刪除成功");
//       loadLatestCustomers();

//     } catch (err) {
//       showError("刪除失敗", err);
//     }
//   }

// async function customerSummary(id) {
//   const el = document.getElementById("summary-result");
//   if (!el) return;

//   try {
//     const data = await api(`/customers/${id}/summary`);
//     el.textContent = JSON.stringify(data, null, 2);
//   } catch (err) {
//     el.textContent = err.message;
//   }
// }

// function clearCustomerForm() {
//   document.getElementById("name").value = "";
//   document.getElementById("phone_number").value = "";
//   document.getElementById("gender").value = "";
//   document.getElementById("birthday").value = "";
//   document.getElementById("note").value = "";
// }


// async function createTransaction() {
//   try {
//     const customerId = document.getElementById("customer_id").value.trim();
//     const catalogSelect = document.getElementById("catalog_item_id");
//     const selectedItem = catalogSelect?.selectedOptions[0];
//     const itemName = selectedItem?.dataset.name || "";

//     if (!itemName) {
//       showError("欄位未完成", "請先選擇消費項目");
//       return;
//     }

//     const payload = {
//       customer_id: customerId ? Number(customerId) : null,
//       note: document.getElementById("tx_note").value || null,
//       items: [{
//         item_name: itemName,
//         qty: Number(document.getElementById("qty").value || 1),
//         unit_price: Number(document.getElementById("unit_price").value || 0),
//       }],
//     };
//     const data = await api("/transactions", {method: "POST", body: JSON.stringify(payload)});
//     await showSuccess("消費新增成功", `交易 ID ${data.id}，總金額 ${data.total_amount}`);
//     document.getElementById("customer_id").value = "";
//     document.getElementById("qty").value = "1";
//     document.getElementById("tx_note").value = "";
//   } catch (err) {
//     showError("新增消費失敗", err);
//   }
// }

// async function listTransactions() {
//   const el = document.getElementById("tx-result");
//   try {
//     const id = document.getElementById("tx_customer_id").value;
//     const data = await api(`/transactions/customer/${id}`);
//     el.textContent = JSON.stringify(data, null, 2);
//   } catch (err) {
//     el.textContent = "";
//     showError("讀取消費紀錄失敗", err);
//   }
// }

// async function loadCatalogItems() {
//   const tbody = document.getElementById("catalog-items-table");
//   if (!tbody) return [];

//   try {
//     const data = await api("/items");
//     tbody.innerHTML = "";

//     for (const item of data) {
//       const tr = document.createElement("tr");
//       tr.innerHTML = `
//         <td>${item.id}</td>
//         <td>${escapeHtml(item.name)}</td>
//         <td>${escapeHtml(item.default_price)}</td>
//         <td>${escapeHtml(item.description || "")}</td>
//       `;
//       tbody.appendChild(tr);
//     }

//     return data;
//   } catch (err) {
//     showError("讀取消費項目失敗", err);
//     return [];
//   }
// }

// async function createCatalogItem() {
//   try {
//     const payload = {
//       name: document.getElementById("catalog_item_name").value.trim(),
//       default_price: Number(document.getElementById("catalog_item_price").value || 0),
//       description: document.getElementById("catalog_item_description").value.trim() || null,
//     };

//     const data = await api("/items", {
//       method: "POST",
//       body: JSON.stringify(payload),
//     });

//     await showSuccess("消費項目新增成功", `${data.name} / ID ${data.id}`);
//     document.getElementById("catalog_item_name").value = "";
//     document.getElementById("catalog_item_price").value = "0";
//     document.getElementById("catalog_item_description").value = "";
//     await loadCatalogItems();
//   } catch (err) {
//     showError("消費項目新增失敗", err);
//   }
// }

// async function loadCatalogOptions() {
//   const select = document.getElementById("catalog_item_id");
//   if (!select) return;

//   try {
//     const data = await api("/items");
//     select.innerHTML = '<option value="">請選擇消費項目</option>';

//     for (const item of data) {
//       const option = document.createElement("option");
//       option.value = item.id;
//       option.textContent = `${item.name}（${item.default_price}）`;
//       option.dataset.name = item.name;
//       option.dataset.price = item.default_price;
//       select.appendChild(option);
//     }
//   } catch (err) {
//     showError("讀取消費項目失敗", err);
//   }
// }

// function applyCatalogItemPrice() {
//   const select = document.getElementById("catalog_item_id");
//   const price = select?.selectedOptions[0]?.dataset.price;
//   if (price !== undefined) {
//     document.getElementById("unit_price").value = price;
//   }
// }

// async function initItemsPage() {
//   if (await checkLoginStatus(true)) {
//     await loadCatalogItems();
//   }
// }

// async function initTransactionsPage() {
//   if (await checkLoginStatus(true)) {
//     await loadCatalogOptions();
//   }
// }

// async function listUsers() {
//   const tbody = document.getElementById("users-table");
//   if (!tbody) return;
//   tbody.innerHTML = "";
//   try {
//     const data = await api("/users");
//     for (const u of data) {
//       const tr = document.createElement("tr");
//       tr.innerHTML = `<td>${u.id}</td><td>${escapeHtml(u.username)}</td><td>${escapeHtml(u.full_name || "")}</td><td>${escapeHtml(u.role)}</td><td>${u.is_active ? "是" : "否"}</td>`;
//       tbody.appendChild(tr);
//     }
//   } catch (err) {
//     showError("讀取人員失敗", err);
//   }
// }

// async function createUser() {
//   try {
//     const payload = {
//       username: document.getElementById("new_username").value,
//       password: document.getElementById("new_password").value,
//       full_name: document.getElementById("new_full_name").value || null,
//       role: document.getElementById("new_role").value,
//       is_active: true,
//     };
//     const data = await api("/users", {method: "POST", body: JSON.stringify(payload)});
//     await showSuccess("新增帳號成功", data.username);
//     await listUsers();
//   } catch (err) {
//     showError("新增帳號失敗", err);
//   }
// }

// async function loadMe() {
//   const el = document.getElementById("me-result");
//   if (!el) return;
//   try {
//     const data = await api("/users/me");
//     el.textContent = JSON.stringify(data, null, 2);
//   } catch (err) {
//     el.textContent = err.message;
//   }
// }

// function escapeHtml(value) {
//   return String(value).replace(/[&<>'"]/g, ch => ({"&":"&amp;","<":"&lt;",">":"&gt;","'":"&#039;","\"":"&quot;"}[ch]));
// }

// async function changeMyPassword() {
//   const oldPassword = document.getElementById("old_password").value;
//   const newPassword = document.getElementById("new_password").value;
//   const confirmPassword = document.getElementById("confirm_password").value;

//   if (!oldPassword || !newPassword || !confirmPassword) {
//     showError("欄位未完成", "請完整輸入所有密碼欄位");
//     return;
//   }

//   if (newPassword !== confirmPassword) {
//     showError("密碼不一致", "新密碼與確認新密碼不一致");
//     return;
//   }

//   try {
//     await api("/users/me/password", {
//       method: "PUT",
//       body: JSON.stringify({
//         old_password: oldPassword,
//         new_password: newPassword,
//       }),
//     });

//     await showSuccess("密碼修改成功，請重新登入");
//     localStorage.removeItem("access_token");

//     setTimeout(() => {
//       goToPage("/login");
//   }, 800);

//   } catch (err) {
//     showError("密碼修改失敗",err);
//   }
// }

// //登入登出
// function updateAuthButton(isLogin) {
//   const btn = document.getElementById("auth-btn");
//   if (!btn) return;

//   if (isLogin) {
//     btn.textContent = "登出";
//   } else {
//     btn.textContent = "登入";
//   }
// }

// function handleAuthButton() {
//   const token = localStorage.getItem("access_token");

//   if (token) {
//     logout();
//   } else {
//     goToPage("/login");
//   }
// }

// //新增csv功能
// async function exportCustomersCsv() {
//   const token = localStorage.getItem("access_token");

//   if (!token) {
//     Swal.fire("請先登入", "", "warning");
//     return;
//   }

//   const res = await fetch("/api/customers/export/csv", {
//     method: "GET",
//     headers: {
//       "Authorization": `Bearer ${token}`,
//     },
//   });

//   if (!res.ok) {
//     Swal.fire("匯出失敗", "請確認權限或重新登入", "error");
//     return;
//   }

//   const blob = await res.blob();
//   const url = window.URL.createObjectURL(blob);

//   const a = document.createElement("a");
//   a.href = url;
//   a.download = "customers.csv";
//   document.body.appendChild(a);
//   a.click();

//   a.remove();
//   window.URL.revokeObjectURL(url);
// }

// // ==================== 頁面跳轉控制 ====================

// // 防止使用者連續點擊，造成重複跳轉。
// let isNavigating = false;

// /**
//  * 統一處理頁面跳轉。
//  *
//  * 原本直接使用 window.location.href 時，
//  * 瀏覽器會立刻切換 HTML，SweetAlert icon 來不及先顯示。
//  *
//  * 現在改成：
//  * 顯示讀取 icon → 等待 400ms → 切換 HTML。
//  */
// function goToPage(url, title = "頁面載入中...") {
//   // 已經準備跳轉時，不再重複執行。
//   if (isNavigating) return;

//   isNavigating = true;

//   // 先在目前頁面顯示 SweetAlert 讀取 icon。
//   showLoading(title);

//   // 等待 400ms，讓瀏覽器有時間把 icon 畫出來。
//   setTimeout(() => {
//     // 告訴下一個頁面：跳轉動畫已顯示過，第一個初始化 API 不要再跳一次 icon。
//     sessionStorage.setItem("page_navigation_loading", "true");
//     window.location.assign(url);
//   }, 400);
// }

// /**
//  * 攔截站內所有 <a href="..."> 連結。
//  *
//  * 原本點擊 <a> 時，瀏覽器會直接切換 HTML，
//  * 所以需要先 preventDefault() 阻止原本跳轉。
//  */
// document.addEventListener("click", function (event) {
//   const link = event.target.closest("a[href]");

//   // 點到的不是連結，不處理。
//   if (!link) return;

//   /*
//    * 下面這些情況保留瀏覽器原本功能：
//    * 1. 事件已經被其他程式處理。
//    * 2. 使用滑鼠中鍵。
//    * 3. 使用 Ctrl、Shift 等按鍵另開分頁。
//    * 4. target="_blank"。
//    * 5. 下載連結。
//    */
//   if (
//     event.defaultPrevented ||
//     event.button !== 0 ||
//     event.ctrlKey ||
//     event.metaKey ||
//     event.shiftKey ||
//     event.altKey ||
//     link.target === "_blank" ||
//     link.hasAttribute("download")
//   ) {
//     return;
//   }

//   const url = new URL(link.href, window.location.href);

//   // 外部網站不攔截，維持原本跳轉方式。
//   if (url.origin !== window.location.origin) return;

//   // 同一頁面的錨點連結不攔截，例如 href="#top"。
//   if (
//     url.pathname === window.location.pathname &&
//     url.search === window.location.search &&
//     url.hash
//   ) {
//     return;
//   }

//   // 阻止 <a> 原本立即切換 HTML 的行為。
//   event.preventDefault();

//   // 改用統一方法：先顯示 icon，再切換 HTML。
//   goToPage(url.href);
// });
// // ================== 頁面跳轉控制結束 ==================


// new version
const API_PREFIX = "/api";

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

  const shouldShowLoading = options.showLoading !== false && !skipInitialLoading;

  if (shouldShowLoading) {
    showLoading();
  }

  try {
    const headers = {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    };

    const currentToken = localStorage.getItem("access_token");

    if (currentToken){
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
      const detail = data && data.detail ? data.detail : `HTTP ${res.status}`;
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
    window.alert(text ? `${title}：${text}` : title);
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
    window.alert(text ? `${title}：${text}` : title);
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

//登入登出
async function checkLoginStatus(redirectWhenMissing = true) {
  const el = document.getElementById("login-status");
  const currentToken = localStorage.getItem("access_token");

  if (!currentToken) {
    if (el) el.textContent = "尚未登入";
    updateAuthButton(false);

    if (redirectWhenMissing) {
          goToPage("/login");
    }

    return false;
  }

  try {
    const me = await api("/auth/me", { showLoading: false });

    if (el) {
      el.textContent = `已登入：${me.username}（${me.role}）`;
    }

    updateAuthButton(true);

    return true;

  } catch (err) {
    localStorage.removeItem("access_token");

    if (el) {
      el.textContent = "登入已失效";
    }

    updateAuthButton(false);

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
        username: document.getElementById("username").value,
        password: document.getElementById("password").value,
      }),
    });
    localStorage.setItem("access_token", data.access_token);
    await showSuccess("登入成功");
    goToPage("/");
  } catch (err) {
    showError("登入失敗", err);
  }
}

function logout() {
  localStorage.removeItem("access_token");
  goToPage("/login");
}

async function seedData() {
  try {
    const data = await api("/setup/seed", {method: "POST"});
    await showSuccess("測試資料建立完成", data.message || "");
  } catch (err) {
    showError("建立測試資料失敗", err);
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

let isCreatingCustomer = false;

async function createCustomer() {
  if (isCreatingCustomer) return;

  isCreatingCustomer = true;

  try {
    const name = document.getElementById("name").value.trim();
    const phoneNumber = document.getElementById("phone_number").value.trim();
    const birthday = document.getElementById("birthday").value;

    if (!name || !phoneNumber || !birthday) {
      showError("欄位未完成", "請填寫姓名、手機與生日");
      return;
    }

    const payload = {
      name,
      phone_number: phoneNumber,
      gender: document.getElementById("gender").value || null,
      birthday,
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
  }finally{
    isCreatingCustomer = false;
  }
}

async function loadLatestCustomers() {
  const tbody = document.getElementById("customer-table");
  if (!tbody) return;

  try {
    const data = await api("/customers/");
    renderCustomerTable(data);
  } catch (err) {
    showError("讀取最新客戶失敗", err);
  }
}

async function searchCustomers() {
  const q = document.getElementById("q").value.trim();

  if (!q) {
    loadLatestCustomers();
    return;
  }

  try {
    const data = await api(`/customers/search/list?q=${encodeURIComponent(q)}`);
    renderCustomerTable(data);
  } catch (err) {
    showError("查詢失敗", err);
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

let isCreatingTransaction = false;

function clearVerifiedTransactionCustomer() {
  const customerId = document.getElementById("customer_id");
  const result = document.getElementById("transaction-customer-result");

  if (customerId) customerId.value = "";
  if (result) {
    result.textContent = "";
    result.classList.add("hidden");
  }
}

function showVerifiedTransactionCustomer(customer) {
  const customerId = document.getElementById("customer_id");
  const result = document.getElementById("transaction-customer-result");

  if (customerId) customerId.value = customer.id;
  if (result) {
    result.textContent = `已找到：${customer.name}／生日：${customer.birthday || "未填"}`;
    result.classList.remove("hidden", "error");
  }
}

async function findTransactionCustomer() {
  const phoneNumber = document.getElementById("tx_phone_number").value.trim();

  if (!phoneNumber) {
    clearVerifiedTransactionCustomer();
    showError("欄位未完成", "請輸入客戶手機");
    return null;
  }

  try {
    const customer = await api(`/customers/by-phone/${encodeURIComponent(phoneNumber)}`);
    showVerifiedTransactionCustomer(customer);
    return customer;
  } catch (err) {
    clearVerifiedTransactionCustomer();
    showError("找不到客戶", err);
    return null;
  }
}

// async function createTransaction() {
//   if (isCreatingTransaction) return;

//   const phoneNumber = document.getElementById("tx_phone_number").value.trim();
//   const itemName = document.getElementById("item_name").value.trim();
//   const qty = Number(document.getElementById("qty").value);
//   const unitPrice = Number(document.getElementById("unit_price").value);

//   if (!phoneNumber || !itemName) {
//     showError("欄位未完成", "請填寫客戶手機與消費項目");
//     return;
//   }

//   if (!Number.isInteger(qty) || qty < 1 || !Number.isFinite(unitPrice) || unitPrice < 0) {
//     showError("欄位格式錯誤", "數量至少為 1，單價不可小於 0");
//     return;
//   }

//   isCreatingTransaction = true;
//   showLoading("驗證客戶並新增消費中...");

//   try {
//     const customer = await api(
//       `/customers/by-phone/${encodeURIComponent(phoneNumber)}`,
//       {showLoading: false},
//     );
//     showVerifiedTransactionCustomer(customer);

//     const payload = {
//       customer_id: customer.id,
//       note: document.getElementById("tx_note").value || null,
//       items: [{
//         item_name: itemName,
//         qty,
//         unit_price: unitPrice,
//       }],
//     };
//     const data = await api("/transactions", {
//       method: "POST",
//       body: JSON.stringify(payload),
//       showLoading: false,
//     });

//     hideLoading();
//     await showSuccess("消費新增成功", `交易 ID ${data.id}，總金額 ${data.total_amount}`);
//     document.getElementById("tx_phone_number").value = "";
//     document.getElementById("item_name").value = "";
//     document.getElementById("qty").value = "1";
//     document.getElementById("tx_note").value = "";
//     clearVerifiedTransactionCustomer();
//   } catch (err) {
//     hideLoading();
//     showError("新增消費失敗", err);
//   } finally {
//     isCreatingTransaction = false;
//   }
// }
async function createTransaction() {
  if (isCreatingTransaction) return;

  const phoneNumber = document.getElementById("tx_phone_number").value.trim();
  const catalogSelect = document.getElementById("catalog_item_id");
  const selectedItem = catalogSelect?.selectedOptions[0];
  const itemName = selectedItem?.dataset.name || "";

  const qty = Number(document.getElementById("qty").value);
  const unitPrice = Number(document.getElementById("unit_price").value);

  if (!phoneNumber || !itemName) {
    showError("欄位未完成", "請填寫客戶手機並選擇消費項目");
    return;
  }

  if (
    !Number.isInteger(qty) ||
    qty < 1 ||
    !Number.isFinite(unitPrice) ||
    unitPrice < 0
  ) {
    showError("欄位格式錯誤", "數量至少為 1，單價不可小於 0");
    return;
  }

  isCreatingTransaction = true;
  showLoading("驗證客戶並新增消費中...");

  try {
    const customer = await api(
      `/customers/by-phone/${encodeURIComponent(phoneNumber)}`,
      {showLoading: false},
    );

    showVerifiedTransactionCustomer(customer);

    const payload = {
      customer_id: customer.id,
      note: document.getElementById("tx_note").value || null,
      items: [{
        item_name: itemName,
        qty,
        unit_price: unitPrice,
      }],
    };

    const data = await api("/transactions", {
      method: "POST",
      body: JSON.stringify(payload),
      showLoading: false,
    });

    hideLoading();

    await showSuccess(
      "消費新增成功",
      `交易 ID ${data.id}，總金額 ${data.total_amount}`,
    );

    document.getElementById("tx_phone_number").value = "";
    catalogSelect.value = "";
    document.getElementById("qty").value = "1";
    document.getElementById("unit_price").value = "0";
    document.getElementById("tx_note").value = "";

    clearVerifiedTransactionCustomer();
  } catch (err) {
    hideLoading();
    showError("新增消費失敗", err);
  } finally {
    isCreatingTransaction = false;
  }
}

async function listTransactions() {
  const el = document.getElementById("tx-result");
  const phoneNumber = document.getElementById("tx_history_phone").value.trim();

  if (!phoneNumber) {
    el.textContent = "";
    showError("欄位未完成", "請輸入客戶手機");
    return;
  }

  showLoading("讀取消費紀錄中...");

  try {
    const customer = await api(
      `/customers/by-phone/${encodeURIComponent(phoneNumber)}`,
      {showLoading: false},
    );
    const data = await api(
      `/transactions/customer/${customer.id}`,
      {showLoading: false},
    );
    hideLoading();
    el.textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    hideLoading();
    el.textContent = "";
    showError("讀取消費紀錄失敗", err);
  }
}

async function loadCatalogItems() {
  const tbody = document.getElementById("catalog-items-table");
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
    showError("讀取消費項目失敗", err);
    return [];
  }
}

async function createCatalogItem() {
  try {
    const payload = {
      name: document.getElementById("catalog_item_name").value.trim(),
      default_price: Number(document.getElementById("catalog_item_price").value || 0),
      description: document.getElementById("catalog_item_description").value.trim() || null,
    };

    const data = await api("/items", {
      method: "POST",
      body: JSON.stringify(payload),
    });

    await showSuccess("消費項目新增成功", `${data.name} / ID ${data.id}`);
    document.getElementById("catalog_item_name").value = "";
    document.getElementById("catalog_item_price").value = "0";
    document.getElementById("catalog_item_description").value = "";
    await loadCatalogItems();
  } catch (err) {
    showError("消費項目新增失敗", err);
  }
}

// let catalogItemSuggestions = [];

// async function loadCatalogSuggestions() {
//   const datalist = document.getElementById("catalog-item-suggestions");
//   if (!datalist) return;

//   try {
//     catalogItemSuggestions = await api("/items");
//     datalist.innerHTML = "";

//     for (const item of catalogItemSuggestions) {
//       const option = document.createElement("option");
//       option.value = item.name;
//       option.label = `預設價格 ${item.default_price}`;
//       datalist.appendChild(option);
//     }
//   } catch (err) {
//     showError("讀取消費項目失敗", err);
//   }
// }

// function applyCatalogItemPrice() {
//   const itemName = document.getElementById("item_name")?.value.trim().toLowerCase();
//   const matchedItem = catalogItemSuggestions.find(
//     item => item.name.toLowerCase() === itemName,
//   );

//   if (matchedItem) {
//     document.getElementById("unit_price").value = matchedItem.default_price;
//   }
// }

async function loadCatalogOptions() {
  const select = document.getElementById("catalog_item_id");
  if (!select) return;

  try {
    const data = await api("/items");

    select.innerHTML = '<option value="">請選擇消費項目</option>';

    if (data.length === 0) {
      const option = document.createElement("option");
      option.value = "";
      option.textContent = "尚未建立消費項目";
      option.disabled = true;
      select.appendChild(option);
      return;
    }

    for (const item of data) {
      const option = document.createElement("option");

      option.value = item.id;
      option.textContent = `${item.name}（預設價格 ${item.default_price}）`;
      option.dataset.name = item.name;
      option.dataset.price = item.default_price;

      select.appendChild(option);
    }
  } catch (err) {
    showError("讀取消費項目失敗", err);
  }
}

function applyCatalogItemPrice() {
  const select = document.getElementById("catalog_item_id");
  const selectedItem = select?.selectedOptions[0];
  const priceInput = document.getElementById("unit_price");

  if (!priceInput) return;

  priceInput.value = selectedItem?.dataset.price ?? "0";
}

async function initItemsPage() {
  if (await checkLoginStatus(true)) {
    await loadCatalogItems();
  }
}

// async function initTransactionsPage() {
//   if (await checkLoginStatus(true)) {
//     await loadCatalogSuggestions();
//   }
// }

async function initTransactionsPage() {
  if (await checkLoginStatus(true)) {
    await loadCatalogOptions();
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
    showError("讀取人員失敗", err);
  }
}

async function createUser() {
  try {
    const payload = {
      username: document.getElementById("new_username").value,
      password: document.getElementById("new_password").value,
      full_name: document.getElementById("new_full_name").value || null,
      role: document.getElementById("new_role").value,
      is_active: true,
    };
    const data = await api("/users", {method: "POST", body: JSON.stringify(payload)});
    await showSuccess("新增帳號成功", data.username);
    await listUsers();
  } catch (err) {
    showError("新增帳號失敗", err);
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
      goToPage("/login");
  }, 800);

  } catch (err) {
    showError("密碼修改失敗",err);
  }
}

//登入登出
function updateAuthButton(isLogin) {
  const btn = document.getElementById("auth-btn");
  if (!btn) return;

  if (isLogin) {
    btn.textContent = "登出";
  } else {
    btn.textContent = "登入";
  }
}

function handleAuthButton() {
  const token = localStorage.getItem("access_token");

  if (token) {
    logout();
  } else {
    goToPage("/login");
  }
}

//新增csv功能
async function exportCustomersCsv() {
  const token = localStorage.getItem("access_token");

  if (!token) {
    Swal.fire("請先登入", "", "warning");
    return;
  }

  const res = await fetch("/api/customers/export/csv", {
    method: "GET",
    headers: {
      "Authorization": `Bearer ${token}`,
    },
  });

  if (!res.ok) {
    Swal.fire("匯出失敗", "請確認權限或重新登入", "error");
    return;
  }

  const blob = await res.blob();
  const url = window.URL.createObjectURL(blob);

  const a = document.createElement("a");
  a.href = url;
  a.download = "customers.csv";
  document.body.appendChild(a);
  a.click();

  a.remove();
  window.URL.revokeObjectURL(url);
}

// ==================== 頁面跳轉控制 ====================

// 防止使用者連續點擊，造成重複跳轉。
let isNavigating = false;

/**
 * 統一處理頁面跳轉。
 *
 * 原本直接使用 window.location.href 時，
 * 瀏覽器會立刻切換 HTML，SweetAlert icon 來不及先顯示。
 *
 * 現在改成：
 * 顯示讀取 icon → 等待 400ms → 切換 HTML。
 */
function goToPage(url, title = "頁面載入中...") {
  // 已經準備跳轉時，不再重複執行。
  if (isNavigating) return;

  isNavigating = true;

  // 先在目前頁面顯示 SweetAlert 讀取 icon。
  showLoading(title);

  // 等待 400ms，讓瀏覽器有時間把 icon 畫出來。
  setTimeout(() => {
    // 告訴下一個頁面：跳轉動畫已顯示過，第一個初始化 API 不要再跳一次 icon。
    sessionStorage.setItem("page_navigation_loading", "true");
    window.location.assign(url);
  }, 400);
}

/**
 * 攔截站內所有 <a href="..."> 連結。
 *
 * 原本點擊 <a> 時，瀏覽器會直接切換 HTML，
 * 所以需要先 preventDefault() 阻止原本跳轉。
 */
document.addEventListener("click", function (event) {
  const link = event.target.closest("a[href]");

  // 點到的不是連結，不處理。
  if (!link) return;

  /*
   * 下面這些情況保留瀏覽器原本功能：
   * 1. 事件已經被其他程式處理。
   * 2. 使用滑鼠中鍵。
   * 3. 使用 Ctrl、Shift 等按鍵另開分頁。
   * 4. target="_blank"。
   * 5. 下載連結。
   */
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

  const url = new URL(link.href, window.location.href);

  // 外部網站不攔截，維持原本跳轉方式。
  if (url.origin !== window.location.origin) return;

  // 同一頁面的錨點連結不攔截，例如 href="#top"。
  if (
    url.pathname === window.location.pathname &&
    url.search === window.location.search &&
    url.hash
  ) {
    return;
  }

  // 阻止 <a> 原本立即切換 HTML 的行為。
  event.preventDefault();

  // 改用統一方法：先顯示 icon，再切換 HTML。
  goToPage(url.href);
});
// ================== 頁面跳轉控制結束 ==================