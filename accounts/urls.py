from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import SginupView

app_name = "accounts"

urlpatterns = [
    path("signup/", SginupView.as_view(), name="signup"),
    path(
        "login/",
        TokenObtainPairView.as_view(),
        name="token_obtain_pair",
    ),
    path(
        "token/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh",
    ),
]
