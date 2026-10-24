from __future__ import annotations

import json
import time
from collections.abc import Iterator

from django.conf import settings
from django.http import StreamingHttpResponse
from django.utils import timezone

from client_portal.schemas import OccupiedSlot
from client_portal.services import ClientRoomOccupancyService
from reservations.constants import RESERVATION_BLOCKING_STATUSES
from reservations.models import Reservation


def _to_slot(reservation: Reservation) -> OccupiedSlot:
    return OccupiedSlot(
        reservation_id=reservation.id,
        room_id=reservation.room_id,
        starts_at=reservation.starts_at,
        ends_at=reservation.ends_at,
        is_blocking=reservation.status in RESERVATION_BLOCKING_STATUSES,
    )


def _format_event(event: str, data) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


class RoomOccupancyEventStream:
    def __init__(self) -> None:
        self._occupancy_service = ClientRoomOccupancyService()
        self._poll_seconds = settings.CLIENT_EVENTS_POLL_SECONDS
        self._heartbeat_seconds = settings.CLIENT_EVENTS_HEARTBEAT_SECONDS
        self._max_seconds = settings.CLIENT_EVENTS_MAX_SECONDS

    def iter_events(self) -> Iterator[str]:
        cursor = timezone.now()
        snapshot = [
            _to_slot(reservation).model_dump(mode="json")
            for reservation in self._occupancy_service.get_occupied_slots()
        ]
        yield f"retry: {settings.CLIENT_EVENTS_RETRY_MS}\n\n"
        yield _format_event("snapshot", snapshot)

        started_at = last_sent_at = time.monotonic()
        while time.monotonic() - started_at < self._max_seconds:
            time.sleep(self._poll_seconds)

            for reservation in self._occupancy_service.get_slot_changes(since=cursor):
                cursor = reservation.updated_at
                last_sent_at = time.monotonic()
                yield _format_event("slot", _to_slot(reservation).model_dump(mode="json"))

            if time.monotonic() - last_sent_at >= self._heartbeat_seconds:
                last_sent_at = time.monotonic()
                yield ": ping\n\n"

    def as_response(self) -> StreamingHttpResponse:
        response = StreamingHttpResponse(self.iter_events(), content_type="text/event-stream")
        response["Cache-Control"] = "no-cache"
        response["X-Accel-Buffering"] = "no"
        return response
