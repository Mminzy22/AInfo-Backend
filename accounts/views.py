from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import SginupSerializer, UserSerializer

User = get_user_model()


# 회원가입 (POST /api/v1/accounts/signup/)
class SginupView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SginupSerializer
    permission_classes = [permissions.AllowAny]  # 누구나 회원가입 가능


# 로그인 (POST /api/v1/accounts/login/)
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """이메일과 비밀번호를 받아 JWT 토큰 발급"""
        email = request.data.get("email")
        password = request.data.get("password")

        user = User.objects.filter(email=email).first()

        if user and user.check_password(password):
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "access_token": str(refresh.access_token),
                    "refresh_token": str(refresh),
                    "user": UserSerializer(user).data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {"error": "이메일 또는 비밀번호가 올바르지 않습니다."},
            status=status.HTTP_401_UNAUTHORIZED,
        )
