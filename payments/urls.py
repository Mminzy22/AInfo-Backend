from django.urls import path

from .views import (
    PayVerify,
    payment_webhook,
)

app_name = "payments"

urlpatterns = [
    path("pay-verify/", PayVerify.as_view(), name="pay_verify"),
    path("webhook/kg/", payment_webhook),
]
