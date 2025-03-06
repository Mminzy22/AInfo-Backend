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
    """회원 프로필 조회 및 수정 직렬화"""

    email = serializers.EmailField(read_only=True)  # 이메일 필드 (읽기 전용)
    is_social = serializers.SerializerMethodField()  # 소셜 로그인 여부 확인

    # 프로필 조회 시 객체 반환
    interests = InterestSerializer(many=True, read_only=True)  # ManyToMany (읽기 전용)
    education_level = EducationLevelSerializer(read_only=True)  # ForeignKey (읽기 전용)
    current_status = CurrentStatusSerializer(read_only=True)  # ForeignKey (읽기 전용)
    location = SubRegionSerializer(read_only=True)  # ForeignKey (읽기 전용)

    # 프로필 수정 시 ID 값만 받기
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
            "interests",  # GET 요청 시 객체 반환
            "interests_ids",  # PUT 요청 시 ID 값으로 업데이트
            "location",  # GET 요청 시 객체 반환
            "location_id",  # PUT 요청 시 ID 값으로 업데이트
            "current_status",  # GET 요청 시 객체 반환
            "current_status_id",  # PUT 요청 시 ID 값으로 업데이트
            "education_level",  # GET 요청 시 객체 반환
            "education_level_id",  # PUT 요청 시 ID 값으로 업데이트
            "is_social",  # 소셜 로그인 여부
            "terms_agree",
            "marketing_agree",
            "created_at",
        ]

    def get_is_social(self, obj):
        """소셜 로그인 여부 확인"""
        return SocialAccount.objects.filter(user=obj).exists()

    def update(self, instance, validated_data):
        """프로필 업데이트 로직"""

        # 관심 분야 업데이트 (ManyToMany 관계)
        if "interests_ids" in validated_data:
            instance.interests.set(validated_data.pop("interests_ids"))

        # ForeignKey 필드 업데이트
        instance.education_level = validated_data.pop(
            "education_level_id", instance.education_level
        )
        instance.current_status = validated_data.pop(
            "current_status_id", instance.current_status
        )
        instance.location = validated_data.pop("location_id", instance.location)

        # 나머지 필드 업데이트
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


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
