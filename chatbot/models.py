import uuid

from django.db import models

from accounts.models import User


class ChatRoom(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, default="새 채팅")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class ChatLog(models.Model):
    role_choices = [
        ("user", "User"),
        ("bot", "Bot"),
    ]
    chatroom = models.ForeignKey(
        ChatRoom, on_delete=models.CASCADE, related_name="chatlogs"
    )
    role = models.CharField(max_length=5, choices=role_choices)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return f"[{self.chatroom.title}] {self.role}: {self.message}"
