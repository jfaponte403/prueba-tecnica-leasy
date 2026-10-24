import json
from datetime import datetime, timedelta

import pytest
from django.utils import timezone

from client_portal.security import ClientTokenService
from client_portal.services import ClientRoomOccupancyService
from reservations.models import Reservation
from reservations.tests.factories import (
    CustomerFactory,
    ReservationFactory,
    RoomFactory,
    UserFactory,
)


@pytest.mark.django_db
def test_login_returns_access_token(client):
    user = UserFactory(email="alice@example.com", username="alice", password="demo1234")
    customer = CustomerFactory(user=user)

    response = client.post(
        "/api/v1/auth/login",
        data={"email": customer.user.email, "password": "demo1234"},
        content_type="application/json",
    )

    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.django_db
def test_me_returns_customer_profile(client):
    customer = CustomerFactory()
    token = ClientTokenService.issue_access_token(customer=customer)

    response = client.get(
        "/api/v1/auth/me",
        HTTP_AUTHORIZATION=f"Bearer {token}",
    )

    assert response.status_code == 200
    assert response.json()["id"] == str(customer.id)


@pytest.mark.django_db
def test_reservation_list_is_scoped_to_customer(client):
    customer = CustomerFactory()
    other_customer = CustomerFactory()
    own_reservation = ReservationFactory(customer=customer)
    ReservationFactory(customer=other_customer)
    token = ClientTokenService.issue_access_token(customer=customer)

    response = client.get(
        "/api/v1/reservations/",
        HTTP_AUTHORIZATION=f"Bearer {token}",
    )

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["id"] == str(own_reservation.id)


@pytest.mark.django_db
def test_create_reservation_returns_created_reservation(client):
    customer = CustomerFactory()
    room = RoomFactory(name="Room A")
    token = ClientTokenService.issue_access_token(customer=customer)

    response = client.post(
        "/api/v1/reservations/",
        data={
            "room_id": str(room.id),
            "starts_at": "2026-04-20T15:00:00-05:00",
            "ends_at": "2026-04-20T17:00:00-05:00",
        },
        content_type="application/json",
        HTTP_AUTHORIZATION=f"Bearer {token}",
    )

    assert response.status_code == 200
    reservation = Reservation.objects.get(customer=customer)
    assert response.json() == {
        "id": str(reservation.id),
        "room_name": "Room A",
        "status": "requested",
        "starts_at": "2026-04-20T15:00:00-05:00",
        "ends_at": "2026-04-20T17:00:00-05:00",
        "cancel_reason": None,
    }


@pytest.mark.django_db
def test_room_list_returns_rooms_ordered_by_name(client):
    customer = CustomerFactory()
    room_b = RoomFactory(name="Room B", floor=2, capacity=8)
    room_a = RoomFactory(name="Room A", floor=1, capacity=4)
    token = ClientTokenService.issue_access_token(customer=customer)

    response = client.get(
        "/api/v1/rooms/",
        HTTP_AUTHORIZATION=f"Bearer {token}",
    )

    assert response.status_code == 200
    assert response.json() == [
        {"id": str(room_a.id), "name": "Room A", "floor": 1, "capacity": 4},
        {"id": str(room_b.id), "name": "Room B", "floor": 2, "capacity": 8},
    ]


@pytest.mark.django_db
def test_room_list_requires_authentication(client):
    response = client.get("/api/v1/rooms/")

    assert response.status_code == 401


def _cancel(client, *, reservation_id, token, reason="Cambio de planes"):
    return client.post(
        f"/api/v1/reservations/{reservation_id}/cancel",
        data={"reason": reason},
        content_type="application/json",
        HTTP_AUTHORIZATION=f"Bearer {token}",
    )


@pytest.mark.django_db
def test_cancel_reservation_cancels_own_reservation_with_reason(client):
    customer = CustomerFactory()
    reservation = ReservationFactory(customer=customer, status="confirmed")
    token = ClientTokenService.issue_access_token(customer=customer)

    response = _cancel(client, reservation_id=reservation.id, token=token, reason="  Viaje  ")

    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"
    assert response.json()["cancel_reason"] == "Viaje"
    reservation.refresh_from_db()
    assert reservation.status == "cancelled"
    assert reservation.cancel_reason == "Viaje"


@pytest.mark.django_db
def test_cancel_reservation_rejects_other_customers_reservation(client):
    customer = CustomerFactory()
    reservation = ReservationFactory(customer=CustomerFactory())
    token = ClientTokenService.issue_access_token(customer=customer)

    response = _cancel(client, reservation_id=reservation.id, token=token)

    assert response.status_code == 400
    assert response.json()["code"] == "reservation_not_found"
    reservation.refresh_from_db()
    assert reservation.status == "requested"


@pytest.mark.django_db
def test_cancel_reservation_requires_reason(client):
    customer = CustomerFactory()
    reservation = ReservationFactory(customer=customer)
    token = ClientTokenService.issue_access_token(customer=customer)

    response = _cancel(client, reservation_id=reservation.id, token=token, reason="   ")

    assert response.status_code == 400
    assert response.json() == {
        "type": "urn:assessment:problem:reservation_cancel_reason_required",
        "title": "Application Error",
        "status": 400,
        "detail": "A cancellation reason is required.",
        "code": "reservation_cancel_reason_required",
        "instance": f"/api/v1/reservations/{reservation.id}/cancel",
        "errors": None,
    }


@pytest.mark.django_db
@pytest.mark.parametrize("status", ["cancelled", "on_hold"])
def test_cancel_reservation_rejects_non_cancellable_status(client, status):
    customer = CustomerFactory()
    reservation = ReservationFactory(customer=customer, status=status)
    token = ClientTokenService.issue_access_token(customer=customer)

    response = _cancel(client, reservation_id=reservation.id, token=token)

    assert response.status_code == 400
    assert response.json()["code"] == "reservation_invalid_transition"


@pytest.mark.django_db
def test_cancel_reservation_requires_authentication(client):
    reservation = ReservationFactory()

    response = client.post(
        f"/api/v1/reservations/{reservation.id}/cancel",
        data={"reason": "x"},
        content_type="application/json",
    )

    assert response.status_code == 401


def _create(client, *, room, token, starts_at, ends_at):
    return client.post(
        "/api/v1/reservations/",
        data={"room_id": str(room.id), "starts_at": starts_at, "ends_at": ends_at},
        content_type="application/json",
        HTTP_AUTHORIZATION=f"Bearer {token}",
    )


@pytest.mark.django_db
@pytest.mark.parametrize("status", ["requested", "confirmed", "on_hold"])
def test_create_reservation_rejects_overlapping_slot_of_other_customer(client, status):
    room = RoomFactory()
    ReservationFactory(
        room=room,
        status=status,
        starts_at=datetime.fromisoformat("2026-04-20T15:00:00-05:00"),
        ends_at=datetime.fromisoformat("2026-04-20T17:00:00-05:00"),
    )
    customer = CustomerFactory()
    token = ClientTokenService.issue_access_token(customer=customer)

    response = _create(
        client,
        room=room,
        token=token,
        starts_at="2026-04-20T16:00:00-05:00",
        ends_at="2026-04-20T18:00:00-05:00",
    )

    assert response.status_code == 400
    assert response.json()["code"] == "reservation_room_unavailable"
    assert not Reservation.objects.filter(customer=customer).exists()


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("starts_at", "ends_at"),
    [
        ("2026-04-20T15:30:00-05:00", "2026-04-20T17:00:00-05:00"),
        ("2026-04-20T15:00:00-05:00", "2026-04-20T16:45:00-05:00"),
    ],
)
def test_create_reservation_requires_whole_hours(client, starts_at, ends_at):
    room = RoomFactory()
    token = ClientTokenService.issue_access_token(customer=CustomerFactory())

    response = _create(client, room=room, token=token, starts_at=starts_at, ends_at=ends_at)

    assert response.status_code == 400
    assert response.json()["code"] == "reservation_not_on_the_hour"
    assert not Reservation.objects.exists()


@pytest.mark.django_db
def test_create_reservation_allows_adjacent_or_cancelled_slots(client):
    room = RoomFactory()
    ReservationFactory(
        room=room,
        starts_at=datetime.fromisoformat("2026-04-20T15:00:00-05:00"),
        ends_at=datetime.fromisoformat("2026-04-20T17:00:00-05:00"),
    )
    ReservationFactory(
        room=room,
        status="cancelled",
        starts_at=datetime.fromisoformat("2026-04-20T17:00:00-05:00"),
        ends_at=datetime.fromisoformat("2026-04-20T19:00:00-05:00"),
    )
    token = ClientTokenService.issue_access_token(customer=CustomerFactory())

    response = _create(
        client,
        room=room,
        token=token,
        starts_at="2026-04-20T17:00:00-05:00",
        ends_at="2026-04-20T19:00:00-05:00",
    )

    assert response.status_code == 200


def _read_events(response) -> list[tuple[str, object]]:
    body = b"".join(response.streaming_content).decode()
    events = []
    for block in body.split("\n\n"):
        lines = dict(line.split(": ", 1) for line in block.splitlines() if line.startswith(("event", "data")))
        if "event" in lines:
            events.append((lines["event"], json.loads(lines["data"])))
    return events


@pytest.mark.django_db
def test_room_occupancy_events_starts_with_snapshot_of_occupied_slots(client, settings):
    settings.CLIENT_EVENTS_MAX_SECONDS = 0
    occupied = ReservationFactory(customer=CustomerFactory())
    ReservationFactory(status="cancelled")
    ReservationFactory(
        starts_at=timezone.now() - timedelta(hours=3),
        ends_at=timezone.now() - timedelta(hours=1),
    )
    token = ClientTokenService.issue_access_token(customer=CustomerFactory())

    response = client.get(
        "/api/v1/rooms/occupancy/events",
        HTTP_AUTHORIZATION=f"Bearer {token}",
    )

    assert response.status_code == 200
    assert response["Content-Type"] == "text/event-stream"
    assert _read_events(response) == [
        (
            "snapshot",
            [
                {
                    "reservation_id": str(occupied.id),
                    "room_id": str(occupied.room_id),
                    "starts_at": occupied.starts_at.isoformat().replace("+00:00", "Z"),
                    "ends_at": occupied.ends_at.isoformat().replace("+00:00", "Z"),
                    "is_blocking": True,
                }
            ],
        )
    ]


@pytest.mark.django_db
def test_room_occupancy_events_requires_authentication(client):
    response = client.get("/api/v1/rooms/occupancy/events")

    assert response.status_code == 401


@pytest.mark.django_db
def test_room_occupancy_slot_changes_include_released_slots():
    since = timezone.now()
    reservation = ReservationFactory()
    reservation.status = "cancelled"
    reservation.save()

    changes = list(ClientRoomOccupancyService().get_slot_changes(since=since))

    assert changes == [reservation]
