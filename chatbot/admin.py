from django.contrib import admin

from .models import ChatLog, ChatRoom


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "title", "created_at")
    search_fields = (
        "user__email",
        "title",
    )


@admin.register(ChatLog)
class ChatLogAdmin(admin.ModelAdmin):
    list_display = ("id", "chatroom", "role", "message", "timestamp")
    search_fields = (
        "chatroom__title",
        "role",
        "message",
    )
