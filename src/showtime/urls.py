from django.urls import path

from showtime.views import ShowtimeListView, ShowtimeSeatsView

urlpatterns = [
    path("", ShowtimeListView.as_view(), name="showtime"),
    path("<uuid:pk>/seats/", ShowtimeSeatsView.as_view(), name="showtime-seats"),
]
