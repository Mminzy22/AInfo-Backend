from django.db import models

from accounts.models import User


class Payment(models.Model):
    product_name = models.CharField(max_length=255, default="100 크레딧")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=20, null=True, blank=True)  # 결제 상태
    payment_id = models.CharField(max_length=100, unique=True)  # 고유 결제번호
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.payment_id} - {self.status}"
