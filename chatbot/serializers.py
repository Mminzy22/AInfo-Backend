from rest_framework import serializers

from .models import ChatLog, ChatRoom


class ChatbotSerializer(serializers.Serializer):
    """
    - 사용자의 메시지를 검증하는 시리얼라이저
    """

    message = serializers.CharField(max_length=500, required=True)


class ChatLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatLog
        fields = "__all__"

    def validate_role(self, value):
        """role 값이 'user' 또는 'bot'만 가능"""
        if value not in ["user", "bot"]:
            raise serializers.ValidationError("role은 'user' 또는 'bot'만 가능합니다.")
        return value


class ChatRoomSerializer(serializers.ModelSerializer):
    chatlogs = ChatLogSerializer(many=True, read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = ChatRoom
        fields = "__all__"

    def validate_title(self, value):
        """채팅방 제목에 공백만 넣는것 방지"""
        if not value.strip():
            raise serializers.ValidationError("채팅방 제목을 입력하세요.")
        return value
