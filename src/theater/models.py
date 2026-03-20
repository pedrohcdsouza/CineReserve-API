from django.db import models

from base.models import AuditModel


class Theater(AuditModel):
    name = models.CharField(max_length=255)
    kind = models.CharField(
        max_length=50,
        choices=(
            ("STANDARD", "Standard"),
            ("IMAX", "IMAX"),
            ("3D", "3D"),
        ),
        help_text="The type of theater (Standard, IMAX, 3D).",
    )

    @property
    def capacity(self):
        return self.seats.count()

    class Meta:

        db_table = "theater"
        verbose_name = "Theater"
        verbose_name_plural = "Theaters"


class Seat(AuditModel):

    row = models.CharField(
        max_length=5, help_text="The row identifier (e.g., A, B, C)."
    )
    number = models.PositiveIntegerField(help_text="The seat number within the row.")
    kind = models.CharField(
        max_length=50,
        choices=(
            ("REGULAR", "Regular"),
            ("VIP", "VIP"),
            ("ACCESSIBLE", "Accessible"),
        ),
        help_text="The type of seat (Regular, VIP, Accessible).",
    )
    theater = models.ForeignKey(
        "theater.Theater",
        on_delete=models.CASCADE,
        related_name="seats",
        help_text="The theater to which this seat belongs.",
    )

    class Meta:
        db_table = "seat"
        verbose_name = "Seat"
        verbose_name_plural = "Seats"
