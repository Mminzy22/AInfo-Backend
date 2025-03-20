import json
import unittest
from unittest.mock import patch
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from django.test import TransactionTestCase
from chatbot.models import ChatRoom, ChatLog
from chatbot.consumers import ChatConsumer
from chatbot.utils import get_chatbot_response
from channels.db import database_sync_to_async
import asyncio


User = get_user_model()


class ChatConsumerTestCase(TransactionTestCase):
    """
    Django Channels WebSocket 테스트 케이스
    """

    @classmethod
    def setUpClass(cls):
        """테스트 클래스 실행 전에 한 번만 실행"""
        super().setUpClass()
        cls.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(cls.loop)

    def setUp(self):
        """각 테스트 실행 전에 실행 (비동기 DB 작업 지원)"""
        self.user = self.loop.run_until_complete(self.create_user())
        self.chatroom = self.loop.run_until_complete(self.create_chatroom(self.user))

    @database_sync_to_async
    def create_user(self):
        """테스트용 사용자 생성 (email 사용)"""
        return User.objects.create_user(
            email="testuser@example.com", password="testpassword"
        )

    @database_sync_to_async
    def create_chatroom(self, user):
        """테스트용 채팅방 생성 (user 필드 사용)"""
        return ChatRoom.objects.create(user=user)

    async def connect_ws(self, room_id, user_id=None):
        """WebSocket Communicator 생성 및 연결"""
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(), f"/ws/chat/{room_id}/"
        )
        communicator.scope["user_id"] = user_id
        communicator.scope["url_route"] = {"kwargs": {"room_id": room_id}}

        connected, _ = await communicator.connect()
        return communicator if connected else None

    def test_websocket_connection_authenticated_user(self):
        """인증된 사용자가 WebSocket에 정상적으로 연결되는지 테스트"""

        async def run_test():
            communicator = await self.connect_ws(self.chatroom.id, self.user.id)
            self.assertIsNotNone(communicator)
            await communicator.disconnect()

        self.loop.run_until_complete(run_test())

    def test_websocket_connection_unauthenticated_user(self):
        """인증되지 않은 사용자가 WebSocket에 접속할 수 없는지 테스트"""

        async def run_test():
            communicator = await self.connect_ws(self.chatroom.id, None)
            self.assertIsNone(communicator)

        self.loop.run_until_complete(run_test())

    def test_invalid_room_id(self):
        """잘못된 채팅방 ID로 접속 시 차단되는지 테스트"""

        async def run_test():
            communicator = await self.connect_ws(
                room_id=9999, user_id=self.user.id
            )  # 존재하지 않는 room_id
            self.assertIsNone(communicator)

        self.loop.run_until_complete(run_test())

    def test_send_chat_history_on_connect(self):
        """WebSocket 연결 시 기존 대화 기록이 정상적으로 전송되는지 테스트"""

        async def run_test():
            await database_sync_to_async(ChatLog.objects.create)(
                chatroom=self.chatroom, role="user", message="이전 메시지"
            )

            communicator = await self.connect_ws(self.chatroom.id, self.user.id)
            self.assertIsNotNone(communicator)

            chat_history = await communicator.receive_json_from()
            self.assertEqual(chat_history["role"], "user")
            self.assertEqual(chat_history["message"], "이전 메시지")

            await communicator.disconnect()

        self.loop.run_until_complete(run_test())

    def test_message_saving_to_db(self):
        """유저 메시지가 DB에 정상적으로 저장되는지 테스트"""

        async def run_test():
            communicator = await self.connect_ws(self.chatroom.id, self.user.id)
            self.assertIsNotNone(communicator)

            message_data = {"message": "안녕"}
            await communicator.send_json_to(message_data)

            await asyncio.sleep(1)  # 메시지가 저장될 시간을 줌

            # chatroom이 실제로 존재하는지 확인 후 메시지 저장 여부 검사
            chatroom_exists = await database_sync_to_async(
                ChatRoom.objects.filter(id=self.chatroom.id).exists
            )()
            self.assertTrue(chatroom_exists, "채팅방이 존재하지 않음!")

            # 메시지가 정상적으로 DB에 저장되었는지 확인
            chatlog_exists = await database_sync_to_async(
                ChatLog.objects.filter(
                    chatroom=self.chatroom, role="user", message="안녕"
                ).exists
            )()
            self.assertTrue(chatlog_exists, "채팅 로그가 DB에 저장되지 않음!")

            await communicator.disconnect()

        self.loop.run_until_complete(run_test())

    def test_message_sending_and_response(self):
        """유저가 메시지를 보내면 챗봇 응답을 정상적으로 받는지 테스트"""

        async def run_test():
            communicator = await self.connect_ws(self.chatroom.id, self.user.id)
            self.assertIsNotNone(communicator)

            message_data = {"message": "안녕"}
            await communicator.send_json_to(message_data)

            with patch(
                "chatbot.utils.get_chatbot_response", return_value=["안녕하세요!"]
            ):
                # 여러 개의 응답을 받을 수 있도록 루프 사용
                while True:
                    response = await communicator.receive_json_from(timeout=10)
                    print("Received Response:", response)  # 디버깅용 출력

                    if response.get("is_streaming") is False:
                        break  # 최종 응답을 받았으면 루프 종료

            self.assertFalse(response["is_streaming"])  # 최종 응답 확인
            await communicator.disconnect()

        self.loop.run_until_complete(run_test())


if __name__ == "__main__":
    unittest.main()
