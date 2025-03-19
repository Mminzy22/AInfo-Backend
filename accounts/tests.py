from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class AccountsTests(APITestCase):
    def setUp(self):
        """테스트용 유저 생성"""
        self.user = User.objects.create_user(
            email="testuser@example.com", password="Test1234!"
        )
        self.login_url = reverse("accounts:token_obtain_pair")
        self.signup_url = reverse("accounts:signup")
        self.logout_url = reverse("accounts:logout")
        self.profile_url = reverse("accounts:profile")
        self.delete_url = reverse("accounts:delete_account")
        self.token_refresh_url = reverse("accounts:token_refresh")

        self.refresh = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh.access_token)
        self.user.email_verified = True
        self.user.save()

    def test_signup(self):
        """회원가입 테스트"""
        data = {
            "email": "newuser@example.com",
            "password": "Newpass123!",
            "terms_agree": True,
            "marketing_agree": False,
        }
        response = self.client.post(self.signup_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email=data["email"]).exists())

    def test_login(self):
        """로그인 테스트"""
        data = {"email": "testuser@example.com", "password": "Test1234!"}
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_token_refresh(self):
        """JWT 토큰 갱신 테스트"""
        data = {"refresh": str(self.refresh)}
        response = self.client.post(self.token_refresh_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_profile_retrieve(self):
        """프로필 조회 테스트"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user.email)

    def test_profile_update(self):
        """프로필 수정 테스트"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        data = {
            "name": "Updated Name",
            "interests_ids": [],
            "location_id": None,
            "current_status_id": None,
            "education_level_id": None,
        }
        response = self.client.put(self.profile_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout(self):
        """로그아웃 테스트"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        data = {"refresh_token": str(self.refresh)}
        response = self.client.post(self.logout_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_account(self):
        """회원 탈퇴 테스트"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(email=self.user.email).exists())
