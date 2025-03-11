from rest_framework import serializers


class ChatbotSerializer(serializers.Serializer):
    """
    - 사용자의 메시지를 검증하는 시리얼라이저
    """

    message = serializers.CharField(max_length=500, required=True)
