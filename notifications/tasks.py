from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mass_mail
from django.db import transaction

from .models import EmailNotification

User = get_user_model()


@shared_task
def send_mail_to_all(title, content, sender_name):

    users = User.objects.filter(terms_agree=True).values_list("email", flat=True)
    email_messages = [
        (title, content, settings.DEFAULT_FROM_EMAIL, [email])
        for email in users
        if email
    ]

    if email_messages:
        try:
            with transaction.atomic():
                send_mass_mail(email_messages, fail_silently=True)
        except Exception as e:
            print(f"Error sending email: {e}")

        # 이메일 발송 기록 저장
        EmailNotification.objects.create(
            title=title, content=content, sender=sender_name  # 관리자의 이름을 저장
        )
