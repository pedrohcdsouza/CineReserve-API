from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from order.serializers import CheckoutSerializer, OrderSerializer
from order.models import Order, Ticker
from showtime.models import Showtime
from theater.models import Seat
from django.conf import settings
from django.db import transaction
import redis

redis_client = redis.from_url(settings.CELERY_BROKER_URL)


class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=CheckoutSerializer, responses={201: OrderSerializer})
    def post(self, request, *args, **kwargs):
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        showtime_id = serializer.validated_data["showtime_id"]
        seats_data = serializer.validated_data["seats"]
        seat_ids = [str(seat["seat_id"]) for seat in seats_data]

        user_id = str(request.user.id)

        try:
            showtime = Showtime.objects.get(id=showtime_id)
        except Showtime.DoesNotExist:
            return Response(
                {"detail": "Showtime not found."}, status=status.HTTP_404_NOT_FOUND
            )

        with transaction.atomic():
            # Verify seats exist and belong to the correct theater
            valid_seats = Seat.objects.filter(id__in=seat_ids, theater=showtime.theater)
            if valid_seats.count() != len(seat_ids):
                return Response(
                    {
                        "detail": "One or more seats are invalid or do not belong to this theater."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Verify DB-level availability
            already_purchased = Ticker.objects.filter(
                showtime=showtime,
                seat__id__in=seat_ids,
                orders__status__in=["CONFIRMED", "PENDING"],
            ).exists()

            if already_purchased:
                return Response(
                    {"detail": "One or more seats are already reserved or purchased."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Verify Redis locks. Either not locked, or locked by the current user.
            # If locked by someone else, deny.
            redis_keys = [f"seat_lock:{showtime_id}:{seat_id}" for seat_id in seat_ids]
            lock_statuses = redis_client.mget(redis_keys)

            for i, lock in enumerate(lock_statuses):
                if lock is not None and lock.decode() != user_id:
                    return Response(
                        {
                            "detail": f"Seat {seat_ids[i]} is temporarily locked by another user."
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            # Create Tickers and Order
            order = Order.objects.create(
                total_price=0,  # Tickets are free
                status="CONFIRMED",
                created_by=request.user,
            )

            for seat in valid_seats:
                ticker = Ticker.objects.create(
                    discount=0, price=0, showtime=showtime, seat=seat
                )
                order.tickers.add(ticker)

            # Remove Redis locks
            if redis_keys:
                redis_client.delete(*redis_keys)

        # Return digital ticket (Order)
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
