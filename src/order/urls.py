from django.urls import path
from order.views import CheckoutView, MyTicketsView

urlpatterns = [
    path("checkout/", CheckoutView.as_view(), name="checkout"),
    path("my-tickets/", MyTicketsView.as_view(), name="my-tickets"),
]
