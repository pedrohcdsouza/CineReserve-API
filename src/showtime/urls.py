from django.urls import path

from showtime.views import ShowtimeListView

urlpatterns = [
    path("", ShowtimeListView.as_view(), name="showtime"),
]
