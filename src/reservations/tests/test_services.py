import pytest

from reservations.constants import RESERVATION_STATUS_CANCELLED, RESERVATION_STATUS_CONFIRMED
from reservations.exceptions import ReservationStatusTransitionError
from reservations.services import ReservationLifecycleService
from reservations.tests.factories import ReservationFactory


@pytest.mark.django_db
def test_confirm_reservation_moves_requested_to_confirmed():
    reservation = ReservationFactory(status="requested")

    ReservationLifecycleService().confirm_reservation(reservation_id=reservation.id)

    reservation.refresh_from_db()
    assert reservation.status == RESERVATION_STATUS_CONFIRMED


@pytest.mark.django_db
def test_confirm_reservation_rejects_invalid_transition():
    reservation = ReservationFactory(status=RESERVATION_STATUS_CANCELLED)

    with pytest.raises(ReservationStatusTransitionError):
        ReservationLifecycleService().confirm_reservation(reservation_id=reservation.id)


@pytest.mark.django_db
def test_cancel_reservation_moves_requested_to_cancelled():
    reservation = ReservationFactory(status="requested")

    ReservationLifecycleService().cancel_reservation(reservation_id=reservation.id)

    reservation.refresh_from_db()
    assert reservation.status == RESERVATION_STATUS_CANCELLED


@pytest.mark.django_db
def test_cancel_reservation_rejects_already_cancelled():
    reservation = ReservationFactory(status=RESERVATION_STATUS_CANCELLED)

    with pytest.raises(ReservationStatusTransitionError):
        ReservationLifecycleService().cancel_reservation(reservation_id=reservation.id)
