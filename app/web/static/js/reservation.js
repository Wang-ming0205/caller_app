const guestBookingForm = document.getElementById("guest-booking-form");
const guestFirstBookingForm = document.getElementById("guest-first-booking-form");
const guestMessage = document.getElementById("guest-result-message");
const guestAppointments = document.getElementById("guest-appointments");
const guestLookupLast3 = document.getElementById("guest-lookup-last3");
const guestLookupBirthday = document.getElementById("guest-lookup-birthday");
const guestLookupCustomer = document.getElementById("guest-lookup-customer");
const guestLookupButton = document.getElementById("guest-lookup-button");
const guestBookingButton = document.getElementById("guest-booking-button");
const guestFieldsets = [
  guestBookingForm.querySelector("fieldset"),
  guestFirstBookingForm.querySelector("fieldset"),
];



let candidateRevision = 0;
let reservationBusy = false;

function postReservation(path, payload) {
  return fetch(`/reservation/${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

async function readReservation(path, payload, errorMessage) {
  const response = await postReservation(path, payload);
  const result = await response.json().catch(() => null);

  if (!response.ok || result === null) {
    throw new Error(
      typeof result?.detail === "string" ? result.detail : errorMessage
    );
  }

  return result;
}

function syncMemberButtons() {
  const hasSelectedCustomer =
    !guestLookupCustomer.disabled && Boolean(guestLookupCustomer.value);

  guestLookupButton.disabled = !hasSelectedCustomer;
  guestBookingButton.disabled = !hasSelectedCustomer;
}

function memberIdentity() {
  return {
    phone_last3: guestLookupLast3.value,
    birthday: guestLookupBirthday.value,
    customer_id: Number(guestLookupCustomer.value),
  };
}

async function loadGuestCandidates() {
  const revision = ++candidateRevision;
  const phoneLast3 = guestLookupLast3.value;
  const birthday = guestLookupBirthday.value;

  guestMessage.textContent = "";
  guestAppointments.replaceChildren();
  guestLookupCustomer.disabled = true;
  guestLookupCustomer.replaceChildren(
    new Option("請先輸入手機末三碼和生日", "")
  );
  syncMemberButtons();

  if (!/^[0-9]{3}$/.test(phoneLast3) || !birthday) return;

  guestLookupCustomer.replaceChildren(new Option("搜尋姓名中…", ""));

  try {
    const candidates = await readReservation(
      "lookup-candidates",
      { phone_last3: phoneLast3, birthday },
      "無法搜尋姓名。"
    );
    if (revision !== candidateRevision) return;

    const placeholder = candidates.length
      ? "請選擇姓名"
      : "找不到符合的姓名";

    guestLookupCustomer.replaceChildren(new Option(placeholder, ""));
    for (const candidate of candidates) {
      guestLookupCustomer.add(
        new Option(candidate.masked_name, candidate.customer_id)
      );
    }

    guestLookupCustomer.disabled = candidates.length === 0;
  } catch {
    if (revision !== candidateRevision) return;
    guestLookupCustomer.replaceChildren(new Option("姓名搜尋失敗", ""));
  }
}

guestLookupLast3.addEventListener("input", loadGuestCandidates);
guestLookupBirthday.addEventListener("change", loadGuestCandidates);
guestLookupCustomer.addEventListener("change", () => {
  guestMessage.textContent = "";
  guestAppointments.replaceChildren();
  syncMemberButtons();
});

async function runReservationAction(message, action, errorMessage) {
  if (reservationBusy) return;

  reservationBusy = true;
  for (const fieldset of guestFieldsets) {
    fieldset.disabled = true;
  }
  guestMessage.textContent = message;
  guestAppointments.replaceChildren();

  try {
    await action();
  } catch (error) {
    guestMessage.textContent = error.message || errorMessage;
  } finally {
    reservationBusy = false;
    for (const fieldset of guestFieldsets) {
      fieldset.disabled = false;
    }
  }
}

guestLookupButton.addEventListener("click", () => {
  if (!guestLookupCustomer.value) return;
  const identity = memberIdentity();

  runReservationAction("查詢中…", async () => {
    const appointments = await readReservation(
      "lookup-by-last3",
      identity,
      "無法讀取預約清單。"
    );
    guestMessage.textContent = appointments.length ? "" : "查無符合的預約。";
    renderGuestAppointments(appointments, identity);
  }, "無法讀取預約清單。");
});

function submitGuestBooking(bookPath, lookupPath, identity, bookingDetails) {
  return runReservationAction("送出中…", async () => {
    const appointment = await readReservation(
      bookPath,
      { ...identity, ...bookingDetails },
      "預約失敗，請確認資料後再試。"
    );
    const confirmation = `預約完成，編號 ${appointment.id}`;
    guestMessage.textContent = confirmation;
    renderGuestAppointments([appointment], identity);

    try {
      const appointments = await readReservation(
        lookupPath,
        identity,
        "無法讀取預約清單。"
      );
      if (appointments.length) {
        renderGuestAppointments(appointments, identity);
      }
    } catch {
      guestMessage.textContent = `${confirmation}。暫時無法載入其他預約。`;
    }
  }, "目前無法預約，請稍後再試。");
}

guestBookingForm.addEventListener("submit", (event) => {
  event.preventDefault();
  if (!guestLookupCustomer.value) return;

  const localTime = document.getElementById("guest-starts-at").value;
  const serviceName = document.getElementById("guest-service").value.trim();

  submitGuestBooking("book-by-last3", "lookup-by-last3", memberIdentity(), {
    starts_at: new Date(localTime).toISOString(),
    service_name: serviceName,
  });
});

guestFirstBookingForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const fields = new FormData(guestFirstBookingForm);
  const identity = {
    phone_number: fields.get("phone_number").trim(),
    birthday: fields.get("birthday"),
  };

  submitGuestBooking("book", "lookup", identity, {
    name: fields.get("name").trim(),
    starts_at: new Date(fields.get("starts_at")).toISOString(),
    service_name: fields.get("service_name").trim(),
  });
});

loadGuestCandidates();



function renderGuestAppointments(appointments, identity) {
  guestAppointments.replaceChildren();

  for (const appointment of appointments) {
    const card = document.createElement("article");
    card.className = "border rounded p-3";

    const date = new Date(appointment.starts_at);
    const time = Number.isNaN(date.getTime())
      ? appointment.starts_at
      : date.toLocaleString("zh-TW", { timeZone: "Asia/Taipei", hour12: false });
    const statusLabels = { booked: "已預約", cancelled: "已取消" };
    const status = document.createElement("div");
    status.textContent =
      `${time}｜${appointment.service_name}｜${statusLabels[appointment.status] ?? appointment.status}`;
    card.append(status);

    if (appointment.status === "booked") {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "btn btn-outline-danger btn-sm mt-2";
      button.textContent = "取消預約";
      button.addEventListener("click", () => {
        cancelGuestAppointment(appointment.id, identity, time, button, status);
      });
      card.append(button);
    }

    guestAppointments.append(card);
  }
}

async function cancelGuestAppointment(appointmentId, identity, time, button, status) {
  if (!window.confirm(`確定取消 ${time} 的預約嗎？`)) return;

  const phoneNumber = identity.phone_number ?? window.prompt(
    "請輸入完整手機號碼以取消預約。"
  )?.trim();

  if (!phoneNumber) return;

  button.disabled = true;
  try {
    const response = await postReservation("cancel", {
      phone_number: phoneNumber,
      birthday: identity.birthday,
      appointment_id: appointmentId,
    });

    if (!response.ok) {
      throw new Error(
        response.status === 404
          ? "手機號碼不符，或這筆預約已無法取消。"
          : "取消失敗，請確認手機號碼後再試。"
      );
    }

    status.textContent = status.textContent.replace(/已預約$/, "已取消");
    button.remove();
    guestMessage.textContent = "預約已取消。";
  } catch (error) {
    guestMessage.textContent = error.message || "取消失敗，請稍後再試。";
    button.disabled = false;
  }
}