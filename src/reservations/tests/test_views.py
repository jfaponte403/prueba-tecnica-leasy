import pytest
from django.urls import reverse

from reservations.tests.factories import ReservationFactory, UserFactory, grant_permission


@pytest.mark.django_db
def test_reservation_list_requires_login(client):
    response = client.get(reverse("reservation_list"))
    assert response.status_code == 302


@pytest.mark.django_db
def test_reservation_list_renders_for_user_with_permission(client):
    reservation = ReservationFactory()
    user = UserFactory()
    grant_permission(user=user, codename="view_reservation")
    client.force_login(user)

    response = client.get(reverse("reservation_list"))

    assert response.status_code == 200
    assert reservation.customer.display_name in response.content.decode()


@pytest.mark.django_db
def test_reservation_confirm_requires_permission(client):
    reservation = ReservationFactory()
    user = UserFactory()
    client.force_login(user)

    response = client.post(reverse("reservation_confirm", args=[reservation.id]))

    assert response.status_code == 403


@pytest.mark.django_db
def test_reservation_cancel_requires_permission(client):
    reservation = ReservationFactory()
    user = UserFactory()
    client.force_login(user)

    response = client.post(reverse("reservation_cancel", args=[reservation.id]))

    assert response.status_code == 403


@pytest.mark.django_db
def test_reservation_cancel_sets_status_cancelled(client):
    reservation = ReservationFactory(status="requested")
    user = UserFactory()
    grant_permission(user=user, codename="change_reservation")
    client.force_login(user)

    client.post(reverse("reservation_cancel", args=[reservation.id]))

    reservation.refresh_from_db()
    assert reservation.status == "cancelled"
