from datetime import datetime, timedelta, timezone
# 3 lines is add package
from sqlalchemy import select
from app.core.database import SessionLocal
from app.models.customer import Customer

import pytest


@pytest.fixture
def guest_identity():
    return {"phone_number": "0912345678", "birthday": "1995-02-05"}


@pytest.fixture
def booking_payload(guest_identity):
    return {
        **guest_identity,
        "name": "預約測試客戶",
        "starts_at": (datetime.now(timezone.utc) + timedelta(days=2))
        .replace(second=0, microsecond=0)
        .isoformat(),
        "service_name": "剪髮",
    }


@pytest.fixture
def booked_appointment(client, booking_payload):
    response = client.post("/reservation/book", json=booking_payload)
    assert response.status_code == 200, response.text
    return response.json()


def test_guest_reservation_page_has_lookup_controls(client):
    response = client.get("/reservation")

    assert response.status_code == 200
    for element_id in (
        "guest-phone",
        "guest-birthday",
        "guest-lookup-button",
        "guest-result-message",
        "guest-appointments",
    ):
        assert f'id="{element_id}"' in response.text
    assert "/static/js/reservation.js" in response.text


def test_guest_can_book_and_lookup_reservation(
    client, guest_identity, booking_payload, booked_appointment
):
    response = client.post("/reservation/lookup", json=guest_identity)

    assert response.status_code == 200, response.text
    appointments = response.json()
    assert [appointment["id"] for appointment in appointments] == [
        booked_appointment["id"]
    ]
    appointment = appointments[0]
    assert appointment["service_name"] == booking_payload["service_name"]
    assert appointment["status"] == "booked"

    # PostgreSQL can serialize a timezone offset while SQLite can return naive UTC.
    actual = datetime.fromisoformat(appointment["starts_at"].replace("Z", "+00:00"))
    if actual.tzinfo is None:
        actual = actual.replace(tzinfo=timezone.utc)
    assert actual == datetime.fromisoformat(booking_payload["starts_at"])

#add new test 261124
def test_member_without_birthday_can_book_lookup_and_cancel(
    client, sample_customer
):
    with SessionLocal() as db:
        customer = db.scalar(
            select(Customer).where(Customer.id == sample_customer["id"])
        )
        customer.birthday = None
        db.commit()

    identity = {
        "phone_number": sample_customer["phone_number"],
        "name": sample_customer["name"],
    }
    payload = {
        **identity,
        "starts_at": (
            datetime.now(timezone.utc) + timedelta(days=2)
        ).isoformat(),
        "service_name": "生日未登記測試",
    }

    booking = client.post("/reservation/book", json=payload)
    assert booking.status_code == 200, booking.text

    lookup = client.post("/reservation/lookup", json=identity)
    assert lookup.status_code == 200, lookup.text
    assert [row["id"] for row in lookup.json()] == [booking.json()["id"]]

    cancel = client.post(
        "/reservation/cancel",
        json={**identity, "appointment_id": booking.json()["id"]},
    )
    assert cancel.status_code == 200, cancel.text
    assert cancel.json() == {"status": "cancelled"}

    lookup_after_cancel = client.post("/reservation/lookup", json=identity)
    assert lookup_after_cancel.status_code == 200, lookup_after_cancel.text
    assert [row["status"] for row in lookup_after_cancel.json()] == ["cancelled"]

@pytest.mark.parametrize(
    "identity_override",
    [{"phone_number": "0987654321"}, {"birthday": "1996-02-05"}],
    ids=["wrong-phone", "wrong-birthday"],
)
def test_guest_cannot_lookup_or_cancel_with_mismatched_identity(
    client, guest_identity, booked_appointment, identity_override
):
    wrong_identity = {**guest_identity, **identity_override}

    lookup = client.post("/reservation/lookup", json=wrong_identity)
    assert lookup.status_code == 200, lookup.text
    assert lookup.json() == []

    cancel = client.post(
        "/reservation/cancel",
        json={**wrong_identity, "appointment_id": booked_appointment["id"]},
    )
    assert cancel.status_code == 404, cancel.text

    lookup = client.post("/reservation/lookup", json=guest_identity)
    assert lookup.status_code == 200, lookup.text
    assert [appointment["status"] for appointment in lookup.json()] == ["booked"]


def test_guest_can_cancel_once_and_lookup_cancelled_reservation(
    client, guest_identity, booked_appointment
):
    payload = {**guest_identity, "appointment_id": booked_appointment["id"]}

    # first = client.post("/reservation/cancel", json=payload)
    #new version
    first = client.post("/reservation/cancel", json=payload)
    assert first.status_code == 200, first.text
    assert first.json() == {"status": "cancelled"}

    second = client.post("/reservation/cancel", json=payload)
    assert second.status_code == 404

    lookup = client.post("/reservation/lookup", json=guest_identity)
    assert lookup.status_code == 200, lookup.text
    assert [appointment["status"] for appointment in lookup.json()] == ["cancelled"]