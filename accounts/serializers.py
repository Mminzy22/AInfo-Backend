from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
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
    region = serializers.StringRelatedField()

    class Meta:
        model = SubRegion
        fields = ["id", "name", "region"]


# 사용자 기본 정보 직렬화
class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(read_only=True)

    # GET 시 객체 반환
    interests = InterestSerializer(many=True, read_only=True)
    education_level = EducationLevelSerializer(read_only=True)
    current_status = CurrentStatusSerializer(read_only=True)
    location = SubRegionSerializer(read_only=True)

    # PUT 시 ID 값 받기
    interests_ids = serializers.PrimaryKeyRelatedField(
        queryset=Interest.objects.all(), many=True, write_only=True
    )
    education_level_id = serializers.PrimaryKeyRelatedField(
        queryset=EducationLevel.objects.all(), write_only=True, allow_null=True
    )
    current_status_id = serializers.PrimaryKeyRelatedField(
        queryset=CurrentStatus.objects.all(), write_only=True, allow_null=True
    )
    location_id = serializers.PrimaryKeyRelatedField(
        queryset=SubRegion.objects.all(), write_only=True, allow_null=True
    )

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "name",
            "birth_date",
            "interests",
            "interests_ids",
            "location",
            "location_id",
            "current_status",
            "current_status_id",
            "education_level",
            "education_level_id",
            "is_social",  # ← allauth 없이 모델 필드로 제공
            "social_type",  # ← 'kakao', 'google' 등
            "terms_agree",
            "marketing_agree",
            "created_at",
        ]

    def update(self, instance, validated_data):
        """프로필 업데이트 로직"""

        # 관심 분야 업데이트 (ManyToMany 관계)
        if "interests_ids" in validated_data:
            instance.interests.set(validated_data.pop("interests_ids"))

        instance.education_level = validated_data.pop(
            "education_level_id", instance.education_level
        )
        instance.current_status = validated_data.pop(
            "current_status_id", instance.current_status
        )
        instance.location = validated_data.pop("location_id", instance.location)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


# 회원가입 직렬화
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

    def validate_password(self, value):
        """
        Django 기본 비밀번호 유효성 검사기 사용.
        실패 시 ValidationError 발생 → 프론트에 전달됨.
        """
        try:
            validate_password(value)  # Django 내부 validator 실행
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)  # 리스트 형태로 반환
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


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
