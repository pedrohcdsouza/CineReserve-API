from rest_framework import serializers
from order.models import Order, Ticker

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