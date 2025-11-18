from django.core.mail import EmailMultiAlternatives
from django.conf import settings


def send_notification_email(subject, message, recipient_email):
    try:
        email = EmailMultiAlternatives(
            subject=subject,
            body=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient_email]
        )
        email.send()
    except Exception as e:
        print("Email sending failed:", str(e))
