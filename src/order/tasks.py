from celery import shared_task
from django.core.mail import send_mail
from order.models import Order
from django.conf import settings


@shared_task
def send_confirmation_email_task(order_id):
    """
    Sends a confirmation email for a confirmed order.
    """
    try:
        order = Order.objects.get(id=order_id)
        user = order.created_by

        # We assume the user has an email.
        # In a real app we'd construct a nice template with the tickets info.
        subject = f"Your Tickets to the Movies! Order #{order.id}"
        message = f"Hello {user.username},\n\nYour order was confirmed! You selected {order.tickers.count()} tickets.\n\nEnjoy the show!"
        recipient_list = [user.email] if user.email else []

        if recipient_list:
            send_mail(
                subject=subject,
                message=message,
                from_email=(
                    settings.DEFAULT_FROM_EMAIL
                    if hasattr(settings, "DEFAULT_FROM_EMAIL")
                    else "no-reply@cinereserve.com"
                ),
                recipient_list=recipient_list,
                fail_silently=False,
            )
            return f"Email sent to {recipient_list}"
        return "User has no email"

    except Order.DoesNotExist:
        return f"Order {order_id} not found."
