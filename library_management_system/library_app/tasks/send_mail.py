from celery import shared_task

from django.core.mail import send_mail


@shared_task
def send_mail_task(subject, message, sender, recipient_list):
    """Calls send mail django function in queue"""

    send_mail(
        subject=subject,
        message=message,
        from_email=sender,
        recipient_list=recipient_list,
    )
