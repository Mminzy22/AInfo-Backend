from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class ChatbotAPITestCase(APITestCase):
    def setUp(self):
        """테스트용 유저 생성"""
        self.user = User.objects.create_user(
            email="testuser@example.com", password="testpassword"
        )
        self.login_url = reverse("accounts:token_obtain_pair")

        # JWT 토큰 발급
        self.refresh = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh.access_token)

        self.url = reverse("chatbot:chat")

    def test_chatbot(self):
        """입력이 주어졌을 때 200 응답과 적절한 데이터를 반환하는지 확인"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        data = {"message": "취업정책 알려줘"}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(
            "data", response.data
        )  # 응답 데이터에 'data' 필드가 포함되어 있는지 확인
