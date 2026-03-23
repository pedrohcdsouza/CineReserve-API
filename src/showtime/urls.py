from django.urls import path

from showtime.views import ShowtimeListView, ShowtimeSeatsView, ShowtimeSeatReserveView

urlpatterns = [
    path("", ShowtimeListView.as_view(), name="showtime"),
    path("<uuid:pk>/seats/", ShowtimeSeatsView.as_view(), name="showtime-seats"),
    path(
        "<uuid:pk>/seats/<uuid:seat_id>/reserve/",
        ShowtimeSeatReserveView.as_view(),
        name="showtime-seat-reserve",
    ),
]
