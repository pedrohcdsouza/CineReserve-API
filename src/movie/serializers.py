from movie.models import Movie
from rest_framework import serializers


class MovieListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ["id", "title", "release_at"]
