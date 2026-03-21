from django.shortcuts import render
from rest_framework.generics import ListAPIView
from showtime.models import Showtime
from showtime.serializers import ShowtimeListSerializer
from showtime.filters import ShowtimeFilterset
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend


@extend_schema(
    request=None,
    responses=ShowtimeListSerializer(many=True),
)
class ShowtimeListView(ListAPIView):
    queryset = Showtime.objects.all()
    serializer_class = ShowtimeListSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ShowtimeFilterset

    def get_permissions(self):
        return [AllowAny()]
