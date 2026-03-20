from django.db import models

from base.models import AuditModel


class Showtime(AuditModel):

    start_at = models.DateTimeField(
        help_text="The date and time when the showtime starts."
    )
    language = models.CharField(
        max_length=50, help_text="The language in which the showtime is conducted."
    )
    kind = models.CharField(
        max_length=50,
        choices=(
            ("REGULAR", "Regular"),
            ("PREVIEW", "Preview"),
            ("PREMIERE", "Premiere"),
        ),
        help_text="The type of showtime (Regular, Preview, Premiere).",
    )
    movie = models.ForeignKey(
        "movie.Movie",
        on_delete=models.CASCADE,
        related_name="showtimes",
        help_text="The movie associated with this showtime.",
    )
    theater = models.ForeignKey(
        "theater.Theater",
        on_delete=models.CASCADE,
        related_name="showtimes",
        help_text="The theater where this showtime is taking place.",
    )

    class Meta:
        db_table = "showtime"
        verbose_name = "Showtime"
        verbose_name_plural = "Showtimes"
