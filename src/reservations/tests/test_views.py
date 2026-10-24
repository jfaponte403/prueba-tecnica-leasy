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


@pytest.mark.django_db
def test_reservation_hold_requires_hold_permission(client):
    reservation = ReservationFactory(status="requested")
    user = UserFactory()
    grant_permission(user=user, codename="change_reservation")
    client.force_login(user)

    response = client.post(
        reverse("reservation_hold", args=[reservation.id]),
        {"reason": "Pendiente de pago"},
    )

    assert response.status_code == 403
    reservation.refresh_from_db()
    assert reservation.status == "requested"


@pytest.mark.django_db
def test_reservation_hold_sets_status_on_hold_with_reason(client):
    reservation = ReservationFactory(status="requested")
    user = UserFactory()
    grant_permission(user=user, codename="view_reservation")
    grant_permission(user=user, codename="hold_reservation")
    client.force_login(user)

    client.post(
        reverse("reservation_hold", args=[reservation.id]),
        {"reason": "Pendiente de pago"},
        follow=True,
    )

    reservation.refresh_from_db()
    assert reservation.status == "on_hold"



@pytest.mark.django_db
def test_reservation_hold_without_reason_keeps_status(client):
    reservation = ReservationFactory(status="requested")
    user = UserFactory()
    grant_permission(user=user, codename="view_reservation")
    grant_permission(user=user, codename="hold_reservation")
    client.force_login(user)

    client.post(
        reverse("reservation_hold", args=[reservation.id]),
        {"reason": "   "},
        follow=True,
    )

    reservation.refresh_from_db()
    assert reservation.status == "requested"

@pytest.mark.django_db
def test_reservation_release_hold_requires_hold_permission(client):
    reservation = ReservationFactory(status="on_hold", hold_reason="Pendiente de pago")
    user = UserFactory()
    grant_permission(user=user, codename="change_reservation")
    client.force_login(user)

    response = client.post(reverse("reservation_release_hold", args=[reservation.id]))

    assert response.status_code == 403
    reservation.refresh_from_db()
    assert reservation.status == "on_hold"


@pytest.mark.django_db
def test_reservation_release_hold_sets_status_requested(client):
    reservation = ReservationFactory(status="on_hold", hold_reason="Pendiente de pago")
    user = UserFactory()
    grant_permission(user=user, codename="view_reservation")
    grant_permission(user=user, codename="hold_reservation")
    client.force_login(user)

    client.post(
        reverse("reservation_release_hold", args=[reservation.id]),
        follow=True,
    )

    reservation.refresh_from_db()
    assert reservation.status == "requested"
    assert reservation.hold_reason == ""
