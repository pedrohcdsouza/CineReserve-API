from movie.filters import MovieFilterset
from movie.models import Movie
from movie.serializers import MovieListSerializer
from drf_spectacular.utils import extend_schema
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend


@extend_schema(
    request=None,
    responses=MovieListSerializer(many=True),
)
class MovieListView(ListAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieListSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = MovieFilterset

    def get_permissions(self):
        return [AllowAny]
