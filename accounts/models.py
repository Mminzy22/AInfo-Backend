from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models


# ---------------------------
# 사용자 매니저 (UserManager)
# ---------------------------
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("이메일을 입력해야 합니다.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


# ---------------------------
# 보조 테이블들
# ---------------------------
class Interest(models.Model):
    """관심 분야 테이블"""

    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name


class EducationLevel(models.Model):
    """최종 학력 테이블"""

    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name


class CurrentStatus(models.Model):
    """현재 상태 테이블"""

    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name


class Region(models.Model):
    """시/도 테이블"""

    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class SubRegion(models.Model):
    """시/군/구 테이블 (Region을 참조)"""

    name = models.CharField(max_length=50)
    region = models.ForeignKey(
        Region, on_delete=models.CASCADE, related_name="subregions"
    )

    def __str__(self):
        return f"{self.region.name} - {self.name}"


# ---------------------------
# 사용자 모델 (User)
# ---------------------------
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    name = models.CharField(max_length=50, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    last_login = models.DateTimeField(blank=True, null=True)
    email_verified = models.BooleanField(default=False)

    # 소셜 로그인 관련
    is_social = models.BooleanField(default=False)
    social_type = models.CharField(max_length=20, blank=True, null=True)  # ex) 'kakao'
    credit = models.IntegerField(default=0)

    # 추가 정보
    interests = models.ManyToManyField(Interest, blank=True)
    education_level = models.ForeignKey(
        EducationLevel, on_delete=models.SET_NULL, null=True, blank=True
    )
    location = models.ForeignKey(
        SubRegion, on_delete=models.SET_NULL, null=True, blank=True
    )
    current_status = models.ForeignKey(
        CurrentStatus, on_delete=models.SET_NULL, null=True, blank=True
    )

    # 동의 항목
    terms_agree = models.BooleanField(default=False)
    marketing_agree = models.BooleanField(default=False)

    # 관리 필드
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.name or 'Unknown'} ({self.email})"
