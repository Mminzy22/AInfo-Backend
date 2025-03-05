"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 4.2.19.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
import environ
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# 환경 변수 로드
env = environ.Env(
    DEBUG=(bool, False)  # DEBUG 값을 boolean으로 변환, 기본값 False
)

# .env 파일 로드
environ.Env.read_env(BASE_DIR / ".env")

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("DJANGO_SECRET_KEY")


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG")

ALLOWED_HOSTS = (
    ["localhost", "127.0.0.1"] if DEBUG else env.list("ALLOWED_HOSTS", default=[])
)


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party apps
    'rest_framework',
    "rest_framework_simplejwt",
    'rest_framework.authtoken',

    'dj_rest_auth',  # REST API 인증 추가

    # Local apps
    'accounts',
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': (
        {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
        if DEBUG
        else env.db("DATABASE_URL")
    )
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Django REST framework settings
REST_FRAMEWORK = {
    # 1. 인증 방식 (JWT + 세션)
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',  # 일반 API
        'rest_framework.authentication.SessionAuthentication',  # Admin 페이지
    ),

    # 2. 기본 권한 (로그인한 사용자만 API 접근 가능)
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),

    # # 3. 페이지네이션 (한 페이지당 10개)
    # 'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    # 'PAGE_SIZE': 10,

    # # 4. 검색 및 필터링 기능
    # 'DEFAULT_FILTER_BACKENDS': [
    #     'django_filters.rest_framework.DjangoFilterBackend',  # 필터링
    #     'rest_framework.filters.SearchFilter',  # 검색
    #     'rest_framework.filters.OrderingFilter',  # 정렬
    # ],

    # # 5. 요청 제한 (과도한 요청 방지)
    # 'DEFAULT_THROTTLE_CLASSES': [
    #     'rest_framework.throttling.AnonRateThrottle',  # 익명 사용자 제한
    #     'rest_framework.throttling.UserRateThrottle',  # 로그인 사용자 제한
    # ],
    # 'DEFAULT_THROTTLE_RATES': {
    #     'anon': '10/minute',  # 익명 사용자는 1분에 10회 요청 가능
    #     'user': '100/minute',  # 로그인한 사용자는 1분에 100회 요청 가능
    # },

    # # 6. API 응답 포맷 (운영에서는 BrowsableAPIRenderer 제거)
    # 'DEFAULT_RENDERER_CLASSES': [
    #     'rest_framework.renderers.JSONRenderer',  # JSON 응답
    #     'rest_framework.renderers.BrowsableAPIRenderer', # HTML 렌더링
    # ],

}
