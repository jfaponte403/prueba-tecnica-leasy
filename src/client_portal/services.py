from __future__ import annotations

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import QuerySet

from client_portal.exceptions import InvalidCredentialsError
from reservations.exceptions import InvalidReservationPeriodError, RoomNotFoundError
from reservations.models import Customer, Reservation, Room


class ClientPortalAuthService:
    def authenticate_client(self, *, email: str, password: str) -> Customer:
        user = User.objects.filter(email=email).select_related("customer_profile").first()
        if user is None or user.is_staff or not hasattr(user, "customer_profile"):
            raise InvalidCredentialsError()

        authenticated = authenticate(username=user.username, password=password)
        if authenticated is None or not authenticated.is_active:
            raise InvalidCredentialsError()

        return authenticated.customer_profile


class ClientRoomQueryService:
    def get_rooms(self) -> QuerySet[Room]:
        return Room.objects.order_by("name")


class ClientReservationQueryService:
    def get_customer_reservations(self, *, customer_id) -> QuerySet[Reservation]:
        return Reservation.objects.filter(customer_id=customer_id).select_related("room")


class ClientReservationCreateService:
    @transaction.atomic
    def create_reservation(
        self,
        *,
        customer: Customer,
        room_id,
        starts_at,
        ends_at,
    ) -> Reservation:
        if ends_at <= starts_at:
            raise InvalidReservationPeriodError()

        room = Room.objects.filter(pk=room_id).first()
        if room is None:
            raise RoomNotFoundError()

        return Reservation.objects.create(
            customer=customer,
            room=room,
            starts_at=starts_at,
            ends_at=ends_at,
        )
