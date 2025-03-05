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


# 회원가입 직렬화 (회원가입에 필요한 필드만 포함)
class SignupSerializer(serializers.ModelSerializer):
    """회원가입 직렬화"""

    password = serializers.CharField(
        write_only=True, min_length=8, style={"input_type": "password"}
    )

    class Meta:
        model = User
        fields = ["email", "password", "name", "terms_agree", "marketing_agree"]

    def validate_terms_agree(self, value):
        """이메일 수집 및 활용 동의는 필수"""
        if not value:
            raise serializers.ValidationError("이메일 수집 및 활용 동의는 필수입니다.")
        return value

    def create(self, validated_data):
        """새로운 사용자 생성"""
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            name=validated_data.get("name", ""),
            terms_agree=validated_data["terms_agree"],
            marketing_agree=validated_data.get("marketing_agree", False),
        )
        return user


# 회원 프로필 수정 직렬화
class ProfileUpdateSerializer(serializers.ModelSerializer):
    """회원 프로필 수정 직렬화"""

    email = serializers.EmailField(read_only=True)  # 이메일 필드 추가 (읽기 전용)

    class Meta:
        model = User
        fields = [
            "email",
            "name",
            "birth_date",
            "interests",
            "location",
            "current_status",
            "education_level",
            "marketing_agree",
        ]
