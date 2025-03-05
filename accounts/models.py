from allauth.socialaccount.models import SocialAccount  # 소셜 로그인 데이터 삭제용
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """일반 사용자 생성"""
        if not email:
            raise ValueError("이메일을 입력해야 합니다.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """슈퍼유저 생성"""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


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


class User(AbstractBaseUser, PermissionsMixin):
    """사용자 모델 (이메일 기반 로그인)"""

    email = models.EmailField(unique=True)  # 이메일 (로그인 ID)
    password = models.CharField(
        max_length=128
    )  # 비밀번호 (AbstractBaseUser에서 제공되지만, ERD 명확성을 위해 기재)
    name = models.CharField(
        max_length=50, blank=True, null=True
    )  # 사용자 이름 (선택 사항)
    birth_date = models.DateField(blank=True, null=True)  # 생년월일 (YYYY-MM-DD 형식)
    last_login = models.DateTimeField(
        blank=True, null=True
    )  # 마지막 로그인 시간 (AbstractBaseUser 기본 제공)
    email_verified = models.BooleanField(default=False)  # 이메일 인증 여부

    # 추가 정보
    interests = models.ManyToManyField(Interest, blank=True)  # 다대다 관계
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
    terms_agree = models.BooleanField(default=False)  # 이메일 수집 및 활용 동의
    marketing_agree = models.BooleanField(default=False)  # 마케팅 및 프로모션 동의

    # 관리 필드
    is_superuser = models.BooleanField(
        default=False
    )  # 슈퍼유저 여부 (PermissionsMixin 기본 제공, 명확성을 위해 기재)
    is_staff = models.BooleanField(
        default=False
    )  # 관리자 여부 (AbstractUser에서는 제공되지만 명확성을 위해 직접 추가)
    created_at = models.DateTimeField(auto_now_add=True)  # 가입일 (자동 저장)
    updated_at = models.DateTimeField(auto_now=True)  # 마지막 수정일 (자동 업데이트)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def delete(self, *args, **kwargs):
        """회원 탈퇴 시 연관된 소셜 계정도 삭제"""
        SocialAccount.objects.filter(user=self).delete()  # 소셜 계정 삭제
        super().delete(*args, **kwargs)  # 사용자 삭제

    def __str__(self):
        return f"{self.name or 'Unknown'} ({self.email})"
