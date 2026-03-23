from celery import shared_task
from django.conf import settings
import redis


@shared_task
def release_seat_lock_task(showtime_id, seat_id):
    """
    Task to auto-release the temporary lock for a seat after the 10-minute timeout.
    This runs asynchronously through Celery.
    """
    redis_client = redis.from_url(settings.CELERY_BROKER_URL)
    lock_key = f"seat_lock:{showtime_id}:{seat_id}"

    # Check if lock still exists and corresponds to a temporary reservation
    lock = redis_client.get(lock_key)
    if lock:
        # We can delete it. Redis `ex` handles it automatically too, but this explicit task fulfills background processing requirements.
        redis_client.delete(lock_key)

    return f"Lock released for showtime {showtime_id}, seat {seat_id}"
