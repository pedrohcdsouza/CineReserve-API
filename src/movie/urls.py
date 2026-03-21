from django.urls import path

from movie.views import MovieListView

urlpatterns = [
    path("", MovieListView.as_view(), name="movie"),
]
