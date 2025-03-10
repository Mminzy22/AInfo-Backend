from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    CurrentStatusListView,
    DeleteAccountView,
    EducationLevelListView,
    InterestListView,
    LogoutView,
    ProfileView,
    SignupView,
    SubRegionListView,
    KakaoLoginView,
)

app_name = "accounts"

urlpatterns = [
    path("signup/", SignupView.as_view(), name="signup"),
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
    path("logout/", LogoutView.as_view(), name="logout"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("subregions/", SubRegionListView.as_view(), name="subregion_list"),
    path("interests/", InterestListView.as_view(), name="interest_list"),
    path(
        "current-statuses/", CurrentStatusListView.as_view(), name="current_status_list"
    ),
    path(
        "education-levels/",
        EducationLevelListView.as_view(),
        name="education_level_list",
    ),
    path("delete/", DeleteAccountView.as_view(), name="delete_account"),

    path("kakao-login/", KakaoLoginView.as_view(), name="kakao_login"),
]
