from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .tokens import token_for_verify_mail

User = get_user_model()


@shared_task
def send_verify_email(user_id, email, domain):
    """
    Description: 메일을 보내는 함수

    - @shared_task 데코레이터를 통해 Celery 를 통한 비동기 처리
    - config/celery.py 에 app.autodiscover_tasks() 설정을 해둬서 다른앱에있는 비동기작업을 자동으로 찾아서 쓰게함
    """
    user = User.objects.get(id=user_id)

    # 이메일 인증을 위한 토큰 생성
    token = token_for_verify_mail.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    # 인증 URL 생성
    mail_subject = "이메일 인증을 완료해주세요."
    message = render_to_string(
        "account/activate_email.html",
        {
            "user": user,
            "domain": domain,
            "uid": uid,
            "token": token,
        },
    )

    send_mail(mail_subject, message, "ainfo.ai.kr@gmail.com", [email])


@shared_task
def send_reset_pw_email(user_id, email, domain):
    user = User.objects.get(id=user_id)

    # 이메일 인증을 위한 토큰 생성
    token = token_for_verify_mail.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    # 인증 URL 생성
    mail_subject = "이메일 인증을 완료해주세요."
    message = render_to_string(
        "account/password_reset_email.html",
        {
            "user": user,
            "domain": domain,
            "uid": uid,
            "token": token,
        },
    )

    send_mail(mail_subject, message, "ainfo.ai.kr@gmail.com", [email])
