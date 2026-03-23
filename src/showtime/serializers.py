from movie.serializers import MovieListSerializer
from showtime.models import Showtime
from theater.models import Seat
from rest_framework import serializers


class ShowtimeListSerializer(serializers.ModelSerializer):
    movie = MovieListSerializer()

    class Meta:
        model = Showtime
        fields = ("id", "movie", "start_at", "theater")


class ShowtimeSeatSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(
        choices=["AVAILABLE", "RESERVED", "PURCHASED"],
        help_text="The availability status of the seat.",
    )

    class Meta:
        model = Seat
        fields = ("id", "row", "number", "kind", "status")
