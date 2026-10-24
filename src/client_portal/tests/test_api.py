import pytest

from client_portal.security import ClientTokenService
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
