from django.shortcuts import render, get_object_or_404
from django.db import models
from django.db.models import Count, Q, Case, When, Value
from django.conf import settings
import redis
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from showtime.models import Showtime
from theater.models import Seat
from showtime.serializers import ShowtimeListSerializer, ShowtimeSeatSerializer
from showtime.filters import ShowtimeFilterset
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

redis_client = redis.from_url(settings.CELERY_BROKER_URL)


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
        data = serializer.data

        # Check Redis for any temporary locks
        seat_ids = [str(seat["id"]) for seat in data if seat["status"] == "AVAILABLE"]
        if seat_ids:
            redis_keys = [f"seat_lock:{pk}:{seat_id}" for seat_id in seat_ids]
            lock_statuses = redis_client.mget(redis_keys)

            # lock_statuses is a list corresponding 1:1 with redis_keys
            for seat_data in data:
                if seat_data["status"] == "AVAILABLE":
                    seat_id_str = str(seat_data["id"])
                    try:
                        idx = seat_ids.index(seat_id_str)
                        if lock_statuses[idx] is not None:
                            seat_data["status"] = "RESERVED"
                    except ValueError:
                        pass

        return Response(data)


@extend_schema(
    request=None,
    responses={
        200: {"description": "Seat successfully locked"},
        400: {"description": "Seat is already reserved or purchased"},
    },
)
class ShowtimeSeatReserveView(APIView):
    def get_permissions(self):
        return [IsAuthenticated()]

    def post(self, request, pk, seat_id, *args, **kwargs):
        showtime = get_object_or_404(Showtime, pk=pk)
        seat = get_object_or_404(Seat, pk=seat_id, theater=showtime.theater)

        # First, check if there's already an active order for it (DB check)
        is_ordered = Seat.objects.filter(
            id=seat.id,
            tickers__showtime=showtime,
            tickers__orders__status__in=["CONFIRMED", "PENDING"],
        ).exists()

        if is_ordered:
            return Response(
                {"detail": "Seat is already reserved or purchased."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Next, try to lock it in Redis
        lock_key = f"seat_lock:{pk}:{seat_id}"
        user_id = str(request.user.id)

        # nx=True ensures the key is only set if it does not already exist
        # ex=600 sets a 10-minute expiration
        acquired = redis_client.set(lock_key, user_id, ex=600, nx=True)

        if not acquired:
            # Maybe the same user is trying to lock it again? We could allow extending the lock,
            # but for this challenge, returning 400 is fine if it's locked.
            current_lock_user = redis_client.get(lock_key)
            if current_lock_user and current_lock_user.decode() == user_id:
                # Refresh the lock if it's the same user
                redis_client.expire(lock_key, 600)
                return Response(
                    {"detail": "Seat lock renewed."}, status=status.HTTP_200_OK
                )

            return Response(
                {"detail": "Seat is temporarily locked by another user."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"detail": "Seat successfully locked."}, status=status.HTTP_200_OK
        )
