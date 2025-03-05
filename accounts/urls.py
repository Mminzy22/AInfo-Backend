from django.urls import path

from .views import SginupView

app_name = "accounts"

urlpatterns = [
    path("signup/", SginupView.as_view(), name="signup"),
]
