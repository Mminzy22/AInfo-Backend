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
