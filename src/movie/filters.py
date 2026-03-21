from django_filters import UUIDFilter
from django_filters import rest_framework as filters
from movie.models import Movie


class MovieFilterset(filters.FilterSet):
    genre = UUIDFilter(field_name="genre__id", lookup_expr="in")
    theater = UUIDFilter(field_name="showtimes__theater__id", lookup_expr="in")

    class Meta:
        model = Movie
        fields = ["title", "genre", "theater"]
