from showtime.models import Showtime
from django_filters import rest_framework as filters


class ShowtimeFilterset(filters.FilterSet):
    movie = filters.UUIDFilter(field_name="movie__id", lookup_expr="in")

    class Meta:
        model = Showtime
        fields = ["movie"]
