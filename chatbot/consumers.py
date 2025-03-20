import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from accounts.models import User

from .memory import ChatHistoryManager
from .models import ChatLog, ChatRoom
from .serializers import ChatbotSerializer
from .utils import get_chatbot_response


class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket을 통한 실시간 채팅을 처리하는 comsumer 클래스

    해당 클래스는 Django Channels의 AsyncWebsocketConsumer를 상속받아
    WebSocket 연결을 관리하고, 사용자 인증 및 AI응답을 처리합니다.

    사용 방식:
    - WebSocket 연결 시 사용자를 인증하고, 인증된 사용자만 채팅 이용 가능
    - 클라이언트가 메시지를 전송하면 Chatbot 모델을 호츌하여 점진적인 응답을 생성
    - `is_streaming=True`로 스트리밍 중임을 같이 알림
    - 생성이 끝나면 완전한 메시지와 'is_streaming=False`도 같이 보내 스트리밍이 끝남을 알림
    - 인증되지 않은 사용자는 메시지를 전송할 수 없으며, 에러 메시지를 반환
    **변동사항(3/20)**
    - WebSocket 연결 시 chatroom_id를 확인하고, 인증된 사용자가 만든 chatroom만 사용 가능
    - user, bot 메시지를 DB에 저장

    매서드(Method)
    - connect(): WebSocket 연결을 초기화하고 사용자 인증을 수행함.
    - disconnect(close_code): Websocket 연결 종료
    - receive(text_data): 클라이언트의 메시지를 받아 Chatbot에 전달
    - get_user(): user_id를 기반으로 데이터베이스에서 사용자 정보 조회
    **변동사항(3/20)**
    - get_chatroom() : chatroom_id를 기반으로 데이터베이스에서 chatroom 정보 조회

    """

    async def connect(self):
        self.user_id = self.scope.get("user_id")
        self.is_authenticated = await self.get_user() is not None

        if not self.is_authenticated:
            await self.close()
            return

        # chatroom pk 확인
        self.room_id = self.scope.get("url_route", {}).get("kwargs", {}).get("room_id")
        if not self.room_id:
            await self.close()
            return

        self.room_group_name = f"chatroom_{self.room_id}"

        # chatroom_id DB조회
        self.chatroom = await self.get_chatroom(self.room_id)
        if not self.chatroom:
            await self.close()
            return

        # WebSocket 그룹 추가
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if self.is_authenticated:
            chat_history_manager = ChatHistoryManager(self.user_id, model=None)
            chat_history_manager.clear_history()

        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        if not self.is_authenticated:
            await self.send(
                text_data=json.dumps(
                    {"error": "인증되지 않은 사용자입니다."},
                    ensure_ascii=False,
                )
            )

        try:
            data = json.loads(text_data)
            user_message = data["message"]
        except json.JSONDecodeError:
            await self.send(
                text_data=json.dumps(
                    {"error": "잘못된 JSON 형식입니다."},
                    ensure_ascii=False,
                )
            )
            return

        serializer = ChatbotSerializer(data={"message": user_message})
        if not serializer.is_valid():
            await self.send(
                text_data=json.dumps(
                    {"error": "잘못된 메시지 형식입니다."},
                    ensure_ascii=False,
                )
            )
            return

        await self.save_message(self.chatroom, "user", user_message)

        bot_message = []  # 청크 저장 할 곳

        # 생성되고 있는 답변의 chunk과 스트리밍 중임을 알림
        async for chunk in get_chatbot_response(user_message, self.user_id):
            bot_message.append(chunk)
            await self.send(
                text_data=json.dumps(
                    {"response": chunk, "is_streaming": True},
                    ensure_ascii=False,
                )
            )

        bot_message_total = "".join(bot_message)
        await self.save_message(self.chatroom, "bot", bot_message_total)

        # 완전히 답변 생성이 끝나면 최종 답변과 스트리밍이 끝남을 알림
        await self.send(
            text_data=json.dumps(
                {"response": bot_message_total, "is_streaming": False},
                ensure_ascii=False,
            )
        )

    @database_sync_to_async
    def get_user(self):
        if self.user_id:
            return User.objects.filter(id=self.user_id).first()
        return None

    @database_sync_to_async
    def get_chatroom(self, room_id):
        """DB에서 room_id에 해당하는 채팅방 가져오기"""
        try:
            return ChatRoom.objects.get(id=room_id)
        except ChatRoom.DoesNotExist:
            return None

    @database_sync_to_async
    def save_message(self, chatroom, role, message):
        """채팅 메시지를 DB에 저장"""
        return ChatLog.objects.create(chatroom=chatroom, role=role, message=message)
