from shared.errors import DomainError


class ReservationError(DomainError):
    code = "reservation_error"
    detail = "Reservation error."


class ReservationNotFoundError(ReservationError):
    code = "reservation_not_found"
    detail = "Reservation not found."


class ReservationStatusTransitionError(ReservationError):
    code = "reservation_invalid_transition"
    detail = "Reservation cannot transition from its current status."


class RoomNotFoundError(ReservationError):
    code = "room_not_found"
    detail = "Room not found."


class InvalidReservationPeriodError(ReservationError):
    code = "reservation_invalid_period"
    detail = "Reservation end must be after its start."


class ReservationNotOnTheHourError(ReservationError):
    code = "reservation_not_on_the_hour"
    detail = "Reservations must start and end on the hour."


class RoomUnavailableError(ReservationError):
    code = "reservation_room_unavailable"
    detail = "The room is already booked for the selected time."


class CancelReasonRequiredError(ReservationError):
    code = "reservation_cancel_reason_required"
    detail = "A cancellation reason is required."


class HoldReasonRequiredError(ReservationError):
    code = "reservation_hold_reason_required"
    detail = "A hold reason is required."
