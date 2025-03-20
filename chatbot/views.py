from django.http import Http404
from rest_framework import generics

from .models import ChatLog, ChatRoom
from .serializers import ChatLogSerializer, ChatRoomSerializer


class BaseChatRoomView(generics.GenericAPIView):
    """모든 채팅방 관련 뷰에서 공통으로 사용하는 get_queryset() 메서드"""

    serializer_class = ChatRoomSerializer

    def get_queryset(self):
        return ChatRoom.objects.filter(user=self.request.user).order_by("-created_at")


class ChatRoomListCreateView(BaseChatRoomView, generics.ListCreateAPIView):
    """채팅방 목록 조회 및 생성"""

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ChatRoomDetailDeleteUpdateView(
    BaseChatRoomView, generics.RetrieveUpdateDestroyAPIView
):
    """채팅방 상세 조회 및 수정(title 변경), 삭제"""

    def get_object(self):
        """로그인한 유저가 본인이 만든 채팅방만 조회/수정/삭제 가능"""
        chatroom_id = self.kwargs.get("pk")
        try:
            return self.get_queryset().get(id=chatroom_id)
        except ChatRoom.DoesNotExist:
            raise Http404("채팅방을 찾을 수 없거나 권한이 없습니다.")


class ChatLogListView(generics.ListAPIView):
    """특정 채팅방의 채팅 로그 조회"""

    serializer_class = ChatLogSerializer

    def get_queryset(self):
        """로그인한 사용자가 소유한 특정 채팅방의 로그만 조회"""
        chatroom_id = self.kwargs.get("pk")
        return ChatLog.objects.filter(chatroom_id=chatroom_id).order_by("timestamp")
