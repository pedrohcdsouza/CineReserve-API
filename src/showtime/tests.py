from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock
from showtime.models import Showtime
from theater.models import Theater, Seat
from movie.models import Movie
from datetime import timedelta
from showtime.tasks import release_seat_lock_task


class ShowtimeTasksUnitTests(TestCase):
    @patch("showtime.tasks.redis")
    def test_release_seat_lock_task(self, mock_redis):
        # Setup Mock Redis
        mock_redis_client = MagicMock()
        mock_redis.from_url.return_value = mock_redis_client
        mock_redis_client.get.return_value = b"test_user_id"

        # Call the task directly
        result = release_seat_lock_task("showtime_1", "seat_1")

        # Check asserts
        mock_redis_client.get.assert_called_with("seat_lock:showtime_1:seat_1")
        mock_redis_client.delete.assert_called_with("seat_lock:showtime_1:seat_1")
        self.assertIn("Lock released", result)


class ShowtimeApiIntegrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.client.force_authenticate(user=self.user)

        self.theater = Theater.objects.create(name="Cine 1", kind="STANDARD")
        self.seat = Seat.objects.create(
            row="A", number=1, kind="REGULAR", theater=self.theater
        )

        self.movie = Movie.objects.create(
            title="Iron Man",
            synopsis="Super hero",
            duration=120,
            release_at="2008-05-02",
            rating="PG-13",
        )

        self.showtime = Showtime.objects.create(
            start_at=timezone.now() + timedelta(days=2),
            language="EN",
            kind="REGULAR",
            movie=self.movie,
            theater=self.theater,
        )

    @patch("showtime.views.redis_client")
    def test_get_showtime_seats(self, mock_redis):
        # Mocking Redis to say no seat is locked
        mock_redis.mget.return_value = [None]

        url = f"/api/showtime/{self.showtime.id}/seats/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return list of 1 seat
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], str(self.seat.id))
        self.assertEqual(response.data[0]["status"], "AVAILABLE")

    @patch("showtime.views.redis_client")
    @patch("showtime.views.release_seat_lock_task.apply_async")
    def test_reserve_seat_integration(self, mock_apply_async, mock_redis):
        # Redis mock allowing acquire lock
        mock_redis.set.return_value = True

        url = f"/api/showtime/{self.showtime.id}/seats/{self.seat.id}/reserve/"
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "Seat successfully locked.")

        # Verify if lock background release was queued
        mock_apply_async.assert_called_once()
        mock_redis.set.assert_called_once()
