from channels.db import database_sync_to_async
from channels.testing import WebsocketCommunicator
from django.test import TestCase
from rest_framework_simplejwt.tokens import AccessToken

from accounts.models import User
from config.asgi import application


class ChatConsumerTest(TestCase):
    """ChatConsumer 테스트"""

    @database_sync_to_async
    def create_user(self):
        """테스트용 가상 사용자 생성"""
        return User.objects.create_user(
            email="testuser@example.com", password="testpassword"
        )

    def create_jwt_token(self, user):
        """사용자에 대해 JWT 토큰 생성"""
        return str(AccessToken.for_user(user))

    async def test_authenticated_user_can_send_and_receive_messages(self):
        """인증된 사용자가 메시지를 보내고 받을 수 있는지 확인"""

        # 테스트용 사용자 생성
        user = await self.create_user()

        # JWT 토큰 생성
        token = self.create_jwt_token(user)

        # WebSocket 연결 시 JWT 토큰을 쿼리 파라미터로 전달
        communicator = WebsocketCommunicator(application, f"ws/chat/?token={token}")
        connected, _ = await communicator.connect()

        # 연결 확인
        self.assertTrue(connected)

        # 사용자 메시지 전송
        message = {"message": "ㅎㅇ"}
        await communicator.send_json_to(message)

        # 챗봇 응답 기다리기
        response = await communicator.receive_json_from(
            timeout=10
        )  # 타임아웃 시간을 10초로 설정
        self.assertIn("response", response)
        self.assertTrue(response["is_streaming"])

        # 스트리밍이 끝날 때까지 대기
        final_response = None
        while True:
            final_response = await communicator.receive_json_from(
                timeout=10
            )  # 스트리밍 종료 확인을 위한 대기
            if not final_response["is_streaming"]:
                break  # 스트리밍이 끝났으면 반복 종료

        # 최종 응답 확인
        self.assertIn("response", final_response)
        self.assertFalse(
            final_response["is_streaming"]
        )  # 이제는 스트리밍이 끝났으므로 False여야 함

        # WebSocket 연결 종료
        await communicator.disconnect()

    async def test_unauthenticated_user_cannot_send_messages(self):
        """인증되지 않은 사용자가 메시지를 보낼 수 없는지 확인"""

        # WebSocket 연결을 시도하지만 인증되지 않은 사용자는 연결이 끊어져야 함
        communicator = WebsocketCommunicator(application, "ws/chat/")
        connected, _ = await communicator.connect()

        # 인증되지 않은 사용자는 연결이 끊어져야 함
        self.assertFalse(connected)

        # 연결 종료
        await communicator.disconnect()

    async def test_invalid_token(self):
        """유효하지 않은 토큰으로 WebSocket 연결 시 실패"""

        # 유효하지 않은 JWT 토큰
        invalid_token = "invalidtoken"

        # WebSocket 연결을 시도하지만 유효하지 않은 토큰으로 연결 시도
        communicator = WebsocketCommunicator(
            application, f"ws/chat/?token={invalid_token}"
        )
        connected, _ = await communicator.connect()

        # 유효하지 않은 토큰으로 연결은 안 되어야 함
        self.assertFalse(connected)

        # 연결 종료
        await communicator.disconnect()

    async def test_no_token(self):
        """토큰이 없으면 WebSocket 연결이 실패해야 함"""

        # 토큰 없이 WebSocket 연결 시도
        communicator = WebsocketCommunicator(application, "ws/chat/")
        connected, _ = await communicator.connect()

        # 토큰이 없으면 연결이 안 되어야 함
        self.assertFalse(connected)

        # 연결 종료
        await communicator.disconnect()
