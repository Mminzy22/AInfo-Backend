from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class EmailNotification(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    sender = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.title
