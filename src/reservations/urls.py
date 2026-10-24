from django.urls import path

from reservations.views import (
    ReservationCancelView,
    ReservationConfirmView,
    ReservationDetailView,
    ReservationHoldView,
    ReservationListView,
    ReservationReleaseHoldView,
    ReservationUpdateView,
)

urlpatterns = [
    path("", ReservationListView.as_view(), name="reservation_list"),
    path("<uuid:pk>/", ReservationDetailView.as_view(), name="reservation_detail"),
    path("<uuid:pk>/edit/", ReservationUpdateView.as_view(), name="reservation_edit"),
    path(
        "<uuid:pk>/confirm/",
        ReservationConfirmView.as_view(),
        name="reservation_confirm",
    ),
    path(
        "<uuid:pk>/cancel/",
        ReservationCancelView.as_view(),
        name="reservation_cancel",
    ),
    path(
        "<uuid:pk>/hold/",
        ReservationHoldView.as_view(),
        name="reservation_hold",
    ),
    path(
        "<uuid:pk>/release-hold/",
        ReservationReleaseHoldView.as_view(),
        name="reservation_release_hold",
    ),
]
