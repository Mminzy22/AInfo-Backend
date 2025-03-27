from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path
from django.utils.html import format_html

from .models import EmailNotification
from .tasks import send_mail_to_all


@admin.register(EmailNotification)
class EmailNotificationAdmin(admin.ModelAdmin):
    list_display = ("title", "content", "sent_at", "sender", "send_email_button")
    readonly_fields = ("sent_at",)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "send-email/<int:email_id>/",
                self.admin_site.admin_view(self.send_email_view),
                name="send_email",
            ),
        ]
        return custom_urls + urls

    def send_email_button(self, obj):
        # 버튼을 클릭하면 이메일 발송 작업을 트리거하는 URL로 이동
        return format_html(
            '<a class="button" href="{}">💌 전체유저에게 공지메일 보내기 💌</a>',
            self.get_send_email_url(obj),
        )

    def get_send_email_url(self, obj):
        # 이메일 발송을 위한 URL 생성 (클릭하면 이메일 발송 작업 실행)
        return f"/admin/notifications/emailnotification/send-email/{obj.id}/"

    def send_email_view(self, request, email_id):
        email_notification = EmailNotification.objects.get(id=email_id)

        # 현재 로그인한 관리자의 이름을 sender 필드에 저장
        email_notification.sender = request.user.name
        email_notification.save()

        send_mail_to_all.delay(
            email_notification.title, email_notification.content, request.user.name
        )

        self.message_user(request, "📨 공지 메일이 전체 사용자에게 전송되었습니다!")
        return redirect(
            "/admin/notifications/emailnotification/"
        )  # 리스트 페이지로 이동
