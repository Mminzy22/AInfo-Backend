from django.contrib.auth.models import BaseUserManager
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
