from __future__ import annotations

from uuid import UUID

from ninja import NinjaAPI, Router
from ninja.errors import ValidationError
from ninja.responses import Status

from client_portal.events import RoomOccupancyEventStream
from client_portal.schemas import (
    ClientProfileSchema,
    LoginRequest,
    ProblemDetailSchema,
    ReservationCancelRequest,
    ReservationCreateRequest,
    ReservationListItem,
    RoomListItem,
    TokenResponse,
)
from client_portal.security import ClientJWTAuth, ClientTokenService
from client_portal.services import (
    ClientPortalAuthService,
    ClientReservationCancelService,
    ClientReservationCreateService,
    ClientReservationQueryService,
    ClientRoomQueryService,
)
from shared.errors import AppError

api = NinjaAPI(title="Assessment Client API", version="1.0.0")
client_auth = ClientJWTAuth()

auth_router = Router(tags=["auth"])
reservation_router = Router(tags=["reservations"])
room_router = Router(tags=["rooms"])

FAMILY_HTTP = {
    "auth": (401, "Authentication Failed"),
    "domain": (400, "Application Error"),
}


@api.exception_handler(AppError)
def handle_app_error(request, exc: AppError):
    status, title = FAMILY_HTTP.get(exc.family, FAMILY_HTTP["domain"])
    problem = ProblemDetailSchema.make(
        request=request,
        status=status,
        code=exc.code,
        title=title,
        detail=exc.detail,
        errors=exc.errors,
    )
    return api.create_response(request, problem.model_dump(), status=status)


@api.exception_handler(ValidationError)
def handle_validation_error(request, exc: ValidationError):
    problem = ProblemDetailSchema.make(
        request=request,
        status=422,
        code="request_validation_error",
        title="Validation Error",
        detail="The request is invalid.",
        errors=exc.errors,
    )
    return api.create_response(request, problem.model_dump(), status=422)


@auth_router.post(
    "/login",
    response={200: TokenResponse, 401: ProblemDetailSchema},
    auth=None,
)
def login(request, payload: LoginRequest):
    customer = ClientPortalAuthService().authenticate_client(
        email=payload.email,
        password=payload.password,
    )
    token = ClientTokenService.issue_access_token(customer=customer)
    return Status(200, TokenResponse(access_token=token))


@auth_router.get("/me", response=ClientProfileSchema, auth=client_auth)
def me(request):
    customer = request.auth
    return ClientProfileSchema(
        id=customer.id,
        email=customer.user.email,
        display_name=customer.display_name,
    )


@reservation_router.get("/", response=list[ReservationListItem], auth=client_auth)
def list_reservations(request):
    reservations = ClientReservationQueryService().get_customer_reservations(
        customer_id=request.auth.id
    )
    return [
        ReservationListItem(
            id=reservation.id,
            room_name=reservation.room.name,
            status=reservation.status,
            starts_at=reservation.starts_at,
            ends_at=reservation.ends_at,
            cancel_reason=reservation.cancel_reason or None,
        )
        for reservation in reservations
    ]


@reservation_router.post(
    "/",
    response={200: ReservationListItem, 400: ProblemDetailSchema, 422: ProblemDetailSchema},
    auth=client_auth,
)
def create_reservation(request, payload: ReservationCreateRequest):
    reservation = ClientReservationCreateService().create_reservation(
        customer=request.auth,
        room_id=payload.room_id,
        starts_at=payload.starts_at,
        ends_at=payload.ends_at,
    )
    return Status(
        200,
        ReservationListItem(
            id=reservation.id,
            room_name=reservation.room.name,
            status=reservation.status,
            starts_at=reservation.starts_at,
            ends_at=reservation.ends_at,
            cancel_reason=reservation.cancel_reason or None,
        ),
    )


@reservation_router.post(
    "/{reservation_id}/cancel",
    response={200: ReservationListItem, 400: ProblemDetailSchema, 422: ProblemDetailSchema},
    auth=client_auth,
)
def cancel_reservation(request, reservation_id: UUID, payload: ReservationCancelRequest):
    reservation = ClientReservationCancelService().cancel_reservation(
        customer=request.auth,
        reservation_id=reservation_id,
        reason=payload.reason,
    )
    return Status(
        200,
        ReservationListItem(
            id=reservation.id,
            room_name=reservation.room.name,
            status=reservation.status,
            starts_at=reservation.starts_at,
            ends_at=reservation.ends_at,
            cancel_reason=reservation.cancel_reason or None,
        ),
    )


@room_router.get("/occupancy/events", auth=client_auth)
def room_occupancy_events(request):
    return RoomOccupancyEventStream().as_response()


@room_router.get("/", response=list[RoomListItem], auth=client_auth)
def list_rooms(request):
    rooms = ClientRoomQueryService().get_rooms()
    return [
        RoomListItem(
            id=room.id,
            name=room.name,
            floor=room.floor,
            capacity=room.capacity,
        )
        for room in rooms
    ]


api.add_router("/auth/", auth_router)
api.add_router("/reservations/", reservation_router)
api.add_router("/rooms/", room_router)
