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
