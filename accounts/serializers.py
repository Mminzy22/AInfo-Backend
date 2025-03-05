from allauth.socialaccount.models import SocialAccount  # 소셜 로그인 여부 확인용
from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import CurrentStatus, EducationLevel, Interest, SubRegion

User = get_user_model()


# 관심 분야 직렬화
class InterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = ["id", "name"]


# 최종 학력 직렬화
class EducationLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = EducationLevel
        fields = ["id", "name"]


# 현재 상태 직렬화
class CurrentStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurrentStatus
        fields = ["id", "name"]


# 시/군/구 직렬화
class SubRegionSerializer(serializers.ModelSerializer):
    region = serializers.StringRelatedField()  # 시/도를 문자열로 반환

    class Meta:
        model = SubRegion
        fields = ["id", "name", "region"]


# 사용자 기본 정보 직렬화
class UserSerializer(serializers.ModelSerializer):
    """기본 사용자 정보 직렬화"""

    is_social = serializers.SerializerMethodField()  # 소셜 로그인 여부 확인
    interests = InterestSerializer(
        many=True, read_only=True
    )  # 다대다 관계 (사용자 관심 분야)
    education_level = EducationLevelSerializer(read_only=True)  # FK
    current_status = CurrentStatusSerializer(read_only=True)  # FK
    location = SubRegionSerializer(read_only=True)  # FK (지역 정보)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "name",
            "birth_date",
            "interests",
            "location",
            "current_status",
            "education_level",
            "is_social",  # 소셜 로그인 여부
            "terms_agree",
            "marketing_agree",
            "created_at",
        ]

    def get_is_social(self, obj):
        """소셜 로그인 여부 확인"""
        return SocialAccount.objects.filter(user=obj).exists()
