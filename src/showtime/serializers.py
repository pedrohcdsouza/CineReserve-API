from movie.serializers import MovieListSerializer
from showtime.models import Showtime
from rest_framework import serializers


class ShowtimeListSerializer(serializers.ModelSerializer):
    movie = MovieListSerializer()

    class Meta:
        model = Showtime
        fields = ("id", "movie", "start_at", "theater")
