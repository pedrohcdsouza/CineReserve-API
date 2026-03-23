from rest_framework import serializers
from order.models import Order, Ticker
from showtime.serializers import ShowtimeListSerializer
from theater.models import Seat


class SimpleSeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seat
        fields = ["id", "row", "number", "kind"]


class TickerDetailSerializer(serializers.ModelSerializer):
    showtime = ShowtimeListSerializer()
    seat = SimpleSeatSerializer()

    class Meta:
        model = Ticker
        fields = ["id", "showtime", "seat", "price", "discount"]


class OrderHistorySerializer(serializers.ModelSerializer):
    tickers = TickerDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ["id", "total_price", "status", "created_by", "tickers", "created_at"]


class TickerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticker
        fields = ["id", "showtime", "seat", "price", "discount"]


class OrderSerializer(serializers.ModelSerializer):
    tickers = TickerSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ["id", "total_price", "status", "created_by", "tickers", "created_at"]


class CheckoutSeatSerializer(serializers.Serializer):
    seat_id = serializers.UUIDField()


class CheckoutSerializer(serializers.Serializer):
    showtime_id = serializers.UUIDField()
    seats = CheckoutSeatSerializer(many=True)
