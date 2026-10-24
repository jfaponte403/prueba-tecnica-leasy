from django.urls import path

from reservations.views import (
    ReservationCancelView,
    ReservationConfirmView,
    ReservationDetailView,
    ReservationListView,
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
]
