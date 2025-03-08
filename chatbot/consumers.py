import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from accounts.models import User

from .utils import get_chatbot_response


class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket을 통한 실시간 채팅을 처리하는 comsumer 클래스

    해당 클래스는 Django Channels의 AsyncWebsocketConsumer를 상속받아
    WebSocket 연결을 관리하고, 사용자 인증 및 AI응답을 처리합니다.

    사용 방식:
    - WebSocket 연결 시 사용자를 인증하고, 인증된 사용자만 채팅 이용 가능
    - 클라이언트가 메시지를 전송하면 Chatbot 모델이 응답을 반환
    - 인증되지 않은 사용자는 메시지를 전송할 수 없으며, 에러 메시지를 반환

    매서드(Method)
    - connect(): WebSocket 연결을 초기화하고 사용자 인증을 수행함.
    - disconnect(close_code): Websocket 연결 종료
    - receive(text_data): 클라이언트의 메시지를 받아 Chatbot에 전달
    - llm_response(user_message): Chatbot에서 응답을 받아옴
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

        llm_response = await self.llm_response(user_message)

        await self.send(
            text_data=json.dumps(
                {"response": llm_response},
                ensure_ascii=False,
            )
        )

    async def llm_response(self, user_message):
        llm_response = get_chatbot_response(user_message)
        response = llm_response.get("response")
        return response

    @sync_to_async
    def get_user(self):
        if self.user_id:
            return User.objects.filter(id=self.user_id).first()
        return None
