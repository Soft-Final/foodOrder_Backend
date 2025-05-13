# app_name/tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_password_async(password: str, targets: list[str]) -> None:
    subject = 'Your Account Password'
    message = f"Your new password is: {password}"

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=targets,
        fail_silently=False
    )
