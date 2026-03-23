from django.shortcuts import render, get_object_or_404
from django.db import models
from django.db.models import Count, Q, Case, When, Value
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from showtime.models import Showtime
from theater.models import Seat
from showtime.serializers import ShowtimeListSerializer, ShowtimeSeatSerializer
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


@extend_schema(
    responses=ShowtimeSeatSerializer(many=True),
)
class ShowtimeSeatsView(APIView):
    def get_permissions(self):
        return [AllowAny()]

    def get(self, request, pk, *args, **kwargs):
        showtime = get_object_or_404(Showtime, pk=pk)

        seats = (
            Seat.objects.filter(theater=showtime.theater)
            .annotate(
                is_purchased=Count(
                    "tickers__orders",
                    filter=Q(
                        tickers__showtime=showtime, tickers__orders__status="CONFIRMED"
                    ),
                ),
                is_reserved=Count(
                    "tickers__orders",
                    filter=Q(
                        tickers__showtime=showtime, tickers__orders__status="PENDING"
                    ),
                ),
            )
            .annotate(
                status=Case(
                    When(is_purchased__gt=0, then=Value("PURCHASED")),
                    When(is_reserved__gt=0, then=Value("RESERVED")),
                    default=Value("AVAILABLE"),
                    output_field=models.CharField(),
                )
            )
        )

        serializer = ShowtimeSeatSerializer(seats, many=True)
        return Response(serializer.data)
