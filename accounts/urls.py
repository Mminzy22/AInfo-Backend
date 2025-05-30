from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    ActivateEmailView,
    AgreeTermsView,
    CreditView,
    CurrentStatusListView,
    DeleteAccountView,
    EducationLevelListView,
    GoogleLoginView,
    InterestListView,
    KakaoLoginView,
    LoginView,
    LogoutView,
    ProfileView,
    ResetPasswordRenderView,
    ResetPasswordView,
    SignupView,
    SubRegionListView,
)

app_name = "accounts"

urlpatterns = [
    path("signup/", SignupView.as_view(), name="signup"),
    path(
        "login/",
        LoginView.as_view(),
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
    path("google-login/", GoogleLoginView.as_view(), name="google_login"),
    path("activate/<uid>/<token>/", ActivateEmailView.as_view(), name="activate_email"),
    path("reset-password/", ResetPasswordView.as_view(), name="reset_password"),
    path(
        "pw-reset/<uid>/<token>/",
        ResetPasswordRenderView.as_view(),
        name="reset_password_render",
    ),
    path("agree-terms/", AgreeTermsView.as_view(), name="agree_terms"),
    path("credit/", CreditView.as_view(), name="user-credit"),
]
