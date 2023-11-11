from datetime import datetime, timezone

from django.conf import settings
from django.utils import timezone

from .send_mail import send_mail_task


def send_otp(email, otp):
    """Send mail on sending ticket request"""

    send_mail_task.apply_async(
        args=[
            "Update password",
            f"You have requested to update your password.\nYou OPT is {otp}. Don't share it with anyone",
            settings.EMAIL_HOST_USER,
            [
                email,
            ],
        ],
        eta=datetime.now(timezone.utc),
    )
