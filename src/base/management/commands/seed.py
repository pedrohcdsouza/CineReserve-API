from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import random

from movie.models import Movie, Genre
from theater.models import Theater, Seat
from showtime.models import Showtime


class Command(BaseCommand):
    help = "Seed the database with sample data for CineReserve"

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding data...")

        # 1. Create a superuser and a normal user
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@cinereserve.com", "admin123")
            self.stdout.write(
                self.style.SUCCESS("Created superuser 'admin' with password 'admin123'")
            )

        user, _ = User.objects.get_or_create(
            username="john_doe", email="john@example.com"
        )
        user.set_password("john123")
        user.save()

        # 2. Create Genres
        genres_data = [
            {
                "title": "Action",
                "description": "Explosions and fights",
                "color": "#FF0000",
            },
            {"title": "Sci-Fi", "description": "Space and future", "color": "#0000FF"},
            {"title": "Drama", "description": "Emotional stories", "color": "#800080"},
        ]
        genres = []
        for g_data in genres_data:
            genre, _ = Genre.objects.get_or_create(
                title=g_data["title"], defaults=g_data
            )
            genres.append(genre)

        # 3. Create Movies
        movies_data = [
            {
                "title": "Interstellar",
                "synopsis": "A team of explorers travel through a wormhole in space in an attempt to ensure humanity's survival.",
                "duration": 169,
                "release_at": "2014-11-07",
                "rating": "PG-13",
                "genres": [genres[1], genres[2]],
            },
            {
                "title": "The Dark Knight",
                "synopsis": "When the menace known as the Joker wreaks havoc and chaos on the people of Gotham.",
                "duration": 152,
                "release_at": "2008-07-18",
                "rating": "PG-13",
                "genres": [genres[0], genres[2]],
            },
        ]

        movies = []
        for m_data in movies_data:
            g = m_data.pop("genres")
            movie, created = Movie.objects.get_or_create(
                title=m_data["title"], defaults=m_data
            )
            if created:
                movie.genres.set(g)
            movies.append(movie)

        # 4. Create Theaters
        theaters_data = [
            {"name": "Room 1 - IMAX", "kind": "IMAX"},
            {"name": "Room 2 - Standard", "kind": "STANDARD"},
        ]
        theaters = []
        for t_data in theaters_data:
            theater, created = Theater.objects.get_or_create(
                name=t_data["name"], defaults=t_data
            )
            theaters.append(theater)

            # 5. Create Seats if theater was just created
            if created:
                for row in ["A", "B", "C"]:
                    for num in range(1, 11):
                        seat_kind = "VIP" if row == "C" else "REGULAR"
                        Seat.objects.create(
                            row=row, number=num, kind=seat_kind, theater=theater
                        )

        # 6. Create Showtimes
        if not Showtime.objects.exists():
            now = timezone.now()

            # Upcoming showtimes
            Showtime.objects.create(
                start_at=now + timedelta(days=1, hours=18),
                language="Legendado",
                kind="PREMIERE",
                movie=movies[0],
                theater=theaters[0],
            )

            Showtime.objects.create(
                start_at=now + timedelta(days=2, hours=20),
                language="Dublado",
                kind="REGULAR",
                movie=movies[1],
                theater=theaters[1],
            )

            # Past showtimes
            Showtime.objects.create(
                start_at=now - timedelta(days=3, hours=14),
                language="Legendado",
                kind="REGULAR",
                movie=movies[0],
                theater=theaters[0],
            )
            self.stdout.write(self.style.SUCCESS("Created showtimes"))

        self.stdout.write(self.style.SUCCESS("Successfully seeded the database!"))
