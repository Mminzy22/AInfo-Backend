"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 4.2.19.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from datetime import timedelta
from pathlib import Path

import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# 환경 변수 로드
env = environ.Env(DEBUG=(bool, False))  # DEBUG 값을 boolean으로 변환, 기본값 False

# .env 파일 로드
environ.Env.read_env(BASE_DIR / ".env")

# ChromaDB 저장 경로 설정
CHROMA_DB_DIR = env("CHROMA_DB_DIR", default=str(BASE_DIR / "chroma_db"))

# API 키 설정
GOV24_API_KEY = env("GOV24_API_KEY")
YOUTH_POLICY_API_KEY = env("YOUTH_POLICY_API_KEY")
EMPLOYMENT_API_KEY = env("EMPLOYMENT_API_KEY")
SEOUL_API_KEY = env("SEOUL_API_KEY")

# PDF 저장 폴더 설정
PDF_DIR = BASE_DIR / "data" / "pdf"

# .env에서 파일명을 불러와서 data/pdf/ 내에서 찾도록 설정
PDF_FILENAME = env("PDF_PATH", default="")
PDF_PATH = str(PDF_DIR / PDF_FILENAME) if PDF_FILENAME else None

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("DJANGO_SECRET_KEY")


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG")

ALLOWED_HOSTS = (
    ["localhost", "127.0.0.1"] if DEBUG else env.list("ALLOWED_HOSTS", default=[])
)


CORS_ALLOWED_ORIGINS = (
    # 프론트엔드가 실행되는 주소 (라이브 서버 플러그인 사용 시)
    ["http://localhost:5500", "http://127.0.0.1:5500"]
    if DEBUG
    else env.list("CORS_ALLOWED_ORIGINS", default=[])
)


# Application definition

INSTALLED_APPS = [
    # Third-party apps
    "daphne",
    "channels",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party apps
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",  # 로그아웃 시 토큰 블랙리스트 사용
    "corsheaders",
    "celery",
    "django_celery_beat",
    # Local apps
    "accounts",
    "chatbot",
    "notifications",
    "payments",
    "dataload",
]


SITE_ID = 1


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",  # corsheaders 미들웨어 추가
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",  # 기본 Django 인증
]


SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
}


# 기본 로그인 필드 설정 (이메일 기반 로그인)
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_VERIFICATION = "none"  # 이메일 인증

GOOGLE_CLIENT_ID = env("GOOGLE_CLIENT_ID")

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR, "templates"],
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
ASGI_APPLICATION = "config.asgi.application"

# Gmail SMTP서버 관련 설정
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = env("EMAIL_PORT")
EMAIL_HOST_USER = env("EMAIL_ID")
EMAIL_HOST_PASSWORD = env("EMAIL_APP_PW")
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = f"AInfo <{EMAIL_HOST_USER}>"
EMAIL_TIMEOUT = 10

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": (
        {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
        if DEBUG
        else env.db("DATABASE_URL")
    )
}


REDIS_HOST = env("REDIS_HOST", default="127.0.0.1")
REDIS_PORT = env.int("REDIS_PORT", default=6379)
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(REDIS_HOST, REDIS_PORT)],
        },
    },
}

# CELERY 관련설정 --> Redis 를 브로커로 설정
CELERY_BROKER_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
CELERY_RESULT_BACKEND = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
# 메시지 직렬화 방식 설정
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"


# 사용자 모델 설정
AUTH_USER_MODEL = "accounts.User"


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

LANGUAGE_CODE = "ko-kr"

TIME_ZONE = "Asia/Seoul"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = "/var/www/AInfo/static/"

MEDIA_URL = "/media/"
MEDIA_ROOT = "/var/www/AInfo/media/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# 기본 권한 설정을 .env에서 불러옴 (DEBUG 모드일 때는 기본적으로 IsAuthenticated)
DEFAULT_PERMISSION_CLASSES = (
    ["rest_framework.permissions.IsAuthenticated"]
    if DEBUG
    else env.list(
        "DEFAULT_PERMISSION_CLASSES",
        default=["rest_framework.permissions.IsAuthenticated"],
    )
)

REST_FRAMEWORK = {
    # 1. 인증 방식 (JWT + 세션)
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",  # 일반 API
        "rest_framework.authentication.SessionAuthentication",  # Admin 페이지
    ),
    # 2. 기본 권한 (로그인한 사용자만 API 접근 가능)
    "DEFAULT_PERMISSION_CLASSES": DEFAULT_PERMISSION_CLASSES,
}
