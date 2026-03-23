from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock
from showtime.models import Showtime
from theater.models import Theater, Seat
from movie.models import Movie
from order.models import Order, Ticker
from order.tasks import send_confirmation_email_task
from datetime import timedelta


class OrderTasksUnitTests(TestCase):
    @patch("order.tasks.send_mail")
    def test_send_confirmation_email_task(self, mock_send_mail):
        # Create dependencies for order
        user = User.objects.create_user(
            username="test", email="test@mail.com", password="pw"
        )
        theater = Theater.objects.create(name="T", kind="STANDARD")
        seat = Seat.objects.create(row="A", number=1, kind="REGULAR", theater=theater)
        movie = Movie.objects.create(
            title="M", synopsis="S", duration=120, release_at="2008-01-01", rating="PG"
        )
        showtime = Showtime.objects.create(
            start_at=timezone.now(),
            language="EN",
            kind="REGULAR",
            movie=movie,
            theater=theater,
        )

        order = Order.objects.create(total_price=0, status="CONFIRMED", created_by=user)
        ticker = Ticker.objects.create(
            discount=0, price=0, showtime=showtime, seat=seat
        )
        order.tickers.add(ticker)

        # Execute celery task synchronously in test
        result = send_confirmation_email_task(str(order.id))

        # Asserts
        self.assertIn("Email sent to", result)
        mock_send_mail.assert_called_once()
        args, kwargs = mock_send_mail.call_args
        self.assertEqual(kwargs["recipient_list"], ["test@mail.com"])


class OrderApiIntegrationTests(TestCase):
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

    @patch("order.views.redis_client")
    @patch("order.views.send_confirmation_email_task.delay")
    def test_checkout_integration(self, mock_delay, mock_redis):
        # Allow checking out regarding redis keys check
        mock_redis.mget.return_value = [None]

        url = "/api/order/checkout/"
        payload = {
            "showtime_id": str(self.showtime.id),
            "seats": [{"seat_id": str(self.seat.id)}],
        }

        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify db commit
        self.assertTrue(Order.objects.filter(created_by=self.user).exists())
        self.assertTrue(
            Ticker.objects.filter(showtime=self.showtime, seat=self.seat).exists()
        )

        # Verify task emit
        mock_delay.assert_called_once()

    def test_my_tickets_integration(self):
        # Create an existing order first
        order = Order.objects.create(
            total_price=0, status="CONFIRMED", created_by=self.user
        )
        ticker = Ticker.objects.create(
            discount=0, price=0, showtime=self.showtime, seat=self.seat
        )
        order.tickers.add(ticker)

        url = "/api/order/my-tickets/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verify pagination/payload returned
        data = response.data["results"] if "results" in response.data else response.data
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], str(order.id))
        self.assertEqual(data[0]["tickers"][0]["showtime"]["id"], str(self.showtime.id))
