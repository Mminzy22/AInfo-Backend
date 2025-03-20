from django.db import models

from accounts.models import User


class ChatRoom(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, default="새 채팅")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
