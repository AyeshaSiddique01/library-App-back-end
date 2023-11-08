from datetime import datetime, timezone

from django.conf import settings

from .send_mail import send_mail_task


def send_update_status_mail(ticket):
    """Send mail on updating the status"""

    send_mail_task.apply_async(
        args=[
            "Request {ticket.status}",
            f"I hope this message finds you well.\nYour request '{ticket.request_message}' has been '{ticket.status}'\n{ticket.response_message}",
            settings.EMAIL_HOST_USER,
            [
                ticket.user.email,
            ],
        ],
        eta=datetime.now(timezone.utc),
    )
