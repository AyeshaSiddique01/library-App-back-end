# from datetime import datetime, timedelta

# from django.conf import settings
# from django.utils import timezone

# from .send_mail import send_mail_task

# def send_request_book_mail(book, user):
#     """Send mail on requesting book"""

#     send_mail_task.apply_async(
#         args=[
#             "Request to return book",
#             f"I hope this message finds you well.\nYou have issued {book.name} on {datetime.now()}. If you have not returned it yet please return it by tomorrow",
#             settings.EMAIL_HOST_USER,
#             [user.email, ]
#         ],
#         eta=datetime.now(timezone.utc) + timedelta(days=15),
#     )
