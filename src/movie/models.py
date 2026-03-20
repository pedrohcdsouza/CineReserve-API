from django.db import models

from base.models import AuditModel


class Movie(AuditModel):
    title = models.CharField(max_length=255)
    synopsis = models.TextField(help_text="A brief summary of the movie plot.")
    duration = models.PositiveIntegerField(
        help_text="Duration of the movie in minutes."
    )
    release_at = models.DateField(help_text="The date when the movie was released.")
    rating = models.CharField(
        max_length=5,
        help_text="The movie's rating (e.g., PG-13, R, etc.).",
    )
    genres = models.ManyToManyField("Genre", related_name="movies")

    class Meta:
        ordering = ["-release_at"]
        db_table = "movie"
        verbose_name = "Movie"
        verbose_name_plural = "Movies"


class Genre(AuditModel):
    title = models.CharField(max_length=255)
    description = models.TextField(help_text="A brief description of the genre.")
    color = models.CharField(
        max_length=7,
        help_text="Hexadecimal color code for the genre (e.g., #FF5733).",
    )
