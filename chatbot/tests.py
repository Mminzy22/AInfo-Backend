from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class ChatbotAPITestCase(APITestCase):
    def setUp(self):
        self.url = reverse("chatbot:chat")

    def test_chatbot(self):
        """입력이 주어졌을 때 200 응답과 적절한 데이터를 반환하는지 확인"""
        data = {"message": "취업정책 알려줘"}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(
            "data", response.data
        )  # 응답 데이터에 'data' 필드가 포함되어 있는지 확인
