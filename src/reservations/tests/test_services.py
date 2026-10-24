from uuid import uuid4

import pytest

from reservations.constants import (
    RESERVATION_STATUS_CANCELLED,
    RESERVATION_STATUS_CONFIRMED,
    RESERVATION_STATUS_ON_HOLD,
    RESERVATION_STATUS_REQUESTED,
)
from reservations.exceptions import (
    HoldReasonRequiredError,
    ReservationNotFoundError,
    ReservationStatusTransitionError,
)
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


@pytest.mark.django_db
@pytest.mark.parametrize(
    "status", [RESERVATION_STATUS_REQUESTED, RESERVATION_STATUS_CONFIRMED]
)
def test_hold_reservation_moves_to_on_hold_with_reason(status):
    reservation = ReservationFactory(status=status)

    ReservationLifecycleService().hold_reservation(
        reservation_id=reservation.id, reason="  Pendiente de pago  "
    )

    reservation.refresh_from_db()
    assert reservation.status == RESERVATION_STATUS_ON_HOLD
    assert reservation.hold_reason == "Pendiente de pago"


@pytest.mark.django_db
@pytest.mark.parametrize("reason", ["", "   "])
def test_hold_reservation_requires_reason(reason):
    reservation = ReservationFactory(status=RESERVATION_STATUS_REQUESTED)

    with pytest.raises(HoldReasonRequiredError):
        ReservationLifecycleService().hold_reservation(
            reservation_id=reservation.id, reason=reason
        )

    reservation.refresh_from_db()
    assert reservation.status == RESERVATION_STATUS_REQUESTED


@pytest.mark.django_db
def test_release_hold_moves_on_hold_to_requested_and_clears_reason():
    reservation = ReservationFactory(
        status=RESERVATION_STATUS_ON_HOLD, hold_reason="Pendiente de pago"
    )

    ReservationLifecycleService().release_hold(reservation_id=reservation.id)

    reservation.refresh_from_db()
    assert reservation.status == RESERVATION_STATUS_REQUESTED
    assert reservation.hold_reason == ""


@pytest.mark.django_db
@pytest.mark.parametrize(
    "status",
    [
        RESERVATION_STATUS_REQUESTED,
        RESERVATION_STATUS_CONFIRMED,
        RESERVATION_STATUS_CANCELLED,
    ],
)
def test_release_hold_rejects_reservation_not_on_hold(status):
    reservation = ReservationFactory(status=status)

    with pytest.raises(ReservationStatusTransitionError):
        ReservationLifecycleService().release_hold(reservation_id=reservation.id)
