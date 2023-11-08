from datetime import datetime, timezone

from django.conf import settings
from django.utils import timezone

from .send_mail import send_mail_task


def send_ticket_mail(ticket, user):
    """Send mail on sending ticket request"""

    send_mail_task.apply_async(
        args=[
            "Request to Add New Book to Library Collection",
            f"I hope this message finds you well.\n{ticket.request_message}",
            user.email,
            [
                settings.EMAIL_HOST_USER,
            ],
        ],
        eta=datetime.now(timezone.utc),
    )
