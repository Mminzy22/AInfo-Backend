from django.contrib.auth import get_user_model
from rest_framework import generics, permissions

from .serializers import SginupSerializer

User = get_user_model()


# 회원가입 (POST /api/v1/accounts/signup/)
class SginupView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SginupSerializer
    permission_classes = [permissions.AllowAny]  # 누구나 회원가입 가능
