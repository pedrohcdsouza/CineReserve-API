from django.db import models

from base.models import AuditModel


class Ticker(AuditModel):
    discount = models.IntegerField(help_text="The discount percentage for the ticket.")
    price = models.IntegerField(help_text="The price of the ticket in cents.")
    showtime = models.ForeignKey(
        "showtime.Showtime",
        on_delete=models.CASCADE,
        related_name="tickers",
        help_text="The showtime associated with this ticket.",
    )
    seat = models.ForeignKey(
        "theater.Seat",
        on_delete=models.CASCADE,
        related_name="tickers",
        help_text="The seat associated with this ticket.",
    )

    class Meta:
        db_table = "ticker"
        verbose_name = "Ticker"
        verbose_name_plural = "Tickers"
        unique_together = ("showtime", "seat")


class Order(AuditModel):
    total_price = models.IntegerField(
        help_text="The total price of the order in cents."
    )
    tickers = models.ManyToManyField(
        "Ticker",
        related_name="orders",
        help_text="The tickets included in this order.",
    )
    status = models.CharField(
        max_length=50,
        choices=(
            ("PENDING", "Pending"),
            ("CONFIRMED", "Confirmed"),
            ("CANCELED", "Canceled"),
        ),
        help_text="The status of the order (Pending, Confirmed, Canceled).",
    )
    created_by = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
        help_text="The user who created the order.",
    )

    class Meta:
        db_table = "order"
        verbose_name = "Order"
        verbose_name_plural = "Orders"
