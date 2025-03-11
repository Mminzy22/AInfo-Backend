import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from accounts.models import User

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

    매서드(Method)
    - connect(): WebSocket 연결을 초기화하고 사용자 인증을 수행함.
    - disconnect(close_code): Websocket 연결 종료
    - receive(text_data): 클라이언트의 메시지를 받아 Chatbot에 전달
    - get_user(): user_id를 기반으로 데이터베이스에서 사용자 정보 조회
    """

    async def connect(self):
        self.user_id = self.scope.get("user_id")
        self.is_authenticated = await self.get_user() is not None

        if not self.is_authenticated:
            await self.close()
            return

        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        if not self.is_authenticated:
            await self.send(
                text_data=json.dumps(
                    {"error": "인증되지 않은 사용자입니다."},
                    ensure_ascii=False,
                )
            )

        data = json.loads(text_data)
        user_message = data["message"]

        serializer = ChatbotSerializer(data={"message": user_message})
        if not serializer.is_valid():
            await self.send(
                text_data=json.dumps(
                    {"error": "잘못된 메시지 형식입니다."},
                    ensure_ascii=False,
                )
            )
            return

        # 생성되고 있는 답변의 chunk과 스트리밍 중임을 알림
        async for chunk in get_chatbot_response(user_message):
            await self.send(
                text_data=json.dumps(
                    {"response": chunk, "is_streaming": True},
                    ensure_ascii=False,
                )
            )

        # 완전히 답변 생성이 끝나면 최종 답변과 스트리밍이 끝남을 알림
        await self.send(
            text_data=json.dumps(
                {"response": chunk, "is_streaming": False},
                ensure_ascii=False,
            )
        )

    @sync_to_async
    def get_user(self):
        if self.user_id:
            return User.objects.filter(id=self.user_id).first()
        return None
