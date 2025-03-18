import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from .tokens import token_for_verify_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes

from .models import CurrentStatus, EducationLevel, Interest, SubRegion
from .serializers import (
    CurrentStatusSerializer,
    EducationLevelSerializer,
    InterestSerializer,
    SignupSerializer,
    SubRegionSerializer,
    UserSerializer,
)

User = get_user_model()


# 회원가입 (POST /api/v1/accounts/signup/)
class SignupView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignupSerializer
    permission_classes = [permissions.AllowAny]  # 누구나 회원가입 가능

    def perform_create(self, serializer):
        """
        Description: 회원가입후 이메일 인증 메일 발송을 위한 함수
        
        - perform_create 메서드를 오버라이딩
        - uid와 tokens.py 에서 작성한 CreateToken 을 통해 만든 token 을 인증메일에 포함
        """
        user = serializer.save()

        # 이메일 인증을 위한 토큰 생성
        token = token_for_verify_mail.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        # 인증 URL 생성
        current_site = get_current_site(self.request)   # 현재 사이트 도메인 가져오기
        mail_subject = '이메일 인증을 완료해주세요.'
        message = render_to_string('account/activate_email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': uid,
            'token': token,
        })
        
        send_mail(mail_subject, message, 'ainfo.ai.kr@gmail.com', [user.email])

        return Response(
            {"message": "회원가입 완료, 이메일 인증을 확인해주세요."},
            status=status.HTTP_201_CREATED,
        )


# 로그인 (POST /api/v1/accounts/login/)
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """이메일과 비밀번호를 받아 JWT 토큰 발급"""
        email = request.data.get("email")
        password = request.data.get("password")

        user = User.objects.filter(email=email).first()
        
        if not user:
            return Response(
                {"error": "이메일 또는 비밀번호가 올바르지 않습니다."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.email_verified:
            return Response(
                {"error": "이메일 본인인증을 완료해주세요"},
                status=status.HTTP_403_FORBIDDEN,
            )

        if user.check_password(password):
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                    "user": UserSerializer(user).data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {"error": "이메일 또는 비밀번호가 올바르지 않습니다."},
            status=status.HTTP_401_UNAUTHORIZED,
        )


# 로그아웃 (POST /api/v1/accounts/logout/)
class LogoutView(APIView):

    def post(self, request):
        """리프레시 토큰을 블랙리스트에 추가하여 로그아웃 처리"""
        try:
            refresh_token = request.data.get("refresh_token")
            token = RefreshToken(refresh_token)
            token.blacklist()  # 토큰 블랙리스트에 추가 (token_blacklist 활성화 필요)
            return Response(
                {"message": "로그아웃되었습니다."}, status=status.HTTP_200_OK
            )
        except Exception:
            return Response(
                {"error": "유효하지 않은 토큰입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )


# 회원 프로필 조회 및 수정 API (GET, PUT /api/v1/accounts/profile/)
class ProfileView(generics.RetrieveUpdateAPIView):
    """회원 프로필 조회 및 수정 API"""

    serializer_class = UserSerializer

    def get_object(self):
        """현재 로그인한 사용자 반환"""
        return self.request.user


# 모든 시/군/구 목록 조회 (GET /api/v1/accounts/subregions/)
class SubRegionListView(generics.ListAPIView):
    """전체 시/군/구 목록 조회 API (시/도 정보 포함)"""

    queryset = SubRegion.objects.all()
    serializer_class = SubRegionSerializer
    permission_classes = [permissions.AllowAny]


# 모든 관심 분야 목록 조회 (GET /api/v1/accounts/interests/)
class InterestListView(generics.ListAPIView):
    """전체 관심 분야 목록 조회 API"""

    queryset = Interest.objects.all()
    serializer_class = InterestSerializer
    permission_classes = [permissions.AllowAny]


# 모든 현재 상태 목록 조회 (GET /api/v1/accounts/current-statuses/)
class CurrentStatusListView(generics.ListAPIView):
    """전체 현재 상태 목록 조회 API"""

    queryset = CurrentStatus.objects.all()
    serializer_class = CurrentStatusSerializer
    permission_classes = [permissions.AllowAny]


# 모든 학력 목록 조회 (GET /api/v1/accounts/education-levels/)
class EducationLevelListView(generics.ListAPIView):
    """전체 학력 목록 조회 API"""

    queryset = EducationLevel.objects.all()
    serializer_class = EducationLevelSerializer
    permission_classes = [permissions.AllowAny]


# 회원 탈퇴 (DELETE /api/v1/accounts/delete/)
class DeleteAccountView(generics.DestroyAPIView):
    """회원 탈퇴 API"""

    def get_object(self):
        """현재 로그인한 사용자 반환"""
        return self.request.user


# 카카오 소셜 로그인 (POST /api/v1/accounts/kakao-login/)
class KakaoLoginView(APIView):
    permission_classes = [permissions.AllowAny]  # 비회원도 접근 가능

    def post(self, request):
        access_token = request.data.get("access_token")
        if not access_token:
            return Response({"error": "Access token이 필요합니다."}, status=400)

        # 1. 카카오 API 호출
        kakao_api = "https://kapi.kakao.com/v2/user/me"
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(kakao_api, headers=headers)

        if response.status_code != 200:
            return Response({"error": "카카오 인증 실패"}, status=400)

        kakao_data = response.json()
        kakao_id = kakao_data.get("id")

        if not kakao_id:
            return Response({"error": "카카오 사용자 정보 없음"}, status=400)

        # 2. 이메일 정보 (없으면 가짜 이메일 생성)
        kakao_account = kakao_data.get("kakao_account", {})
        email = kakao_account.get("email") or f"kakao_{kakao_id}@kakao.com"

        # 3. 사용자 확인 또는 생성
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "password": User.objects.make_random_password(),
                "is_social": True,
                "social_type": "kakao",
                "name": kakao_data.get("properties", {}).get("nickname", ""),
            },
        )

        # 4. JWT 발급
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": {
                    "email": user.email,
                    "name": user.name,
                    "is_social": user.is_social,
                    "social_type": user.social_type,
                },
            },
            status=200,
        )


class GoogleLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        id_token = request.data.get("id_token")
        if not id_token:
            return Response({"error": "ID Token이 필요합니다."}, status=400)

        try:
            # 1. 구글 ID 토큰 검증 (구글 서버의 공개 키로 검증됨)
            idinfo = google_id_token.verify_oauth2_token(
                id_token,
                google_requests.Request(),
                audience=settings.GOOGLE_CLIENT_ID,  # 보통은 CLIENT_ID를 넣는 것이 권장됨
            )
        except ValueError:
            return Response({"error": "유효하지 않은 ID 토큰입니다."}, status=400)

        # 2. 사용자 정보 추출
        email = idinfo.get("email")
        name = idinfo.get("name", "")
        if not email:
            return Response({"error": "구글 이메일 정보가 없습니다."}, status=400)

        # 3. 사용자 확인 또는 생성
        user, _ = User.objects.get_or_create(
            email=email,
            defaults={
                "password": User.objects.make_random_password(),
                "is_social": True,
                "social_type": "google",
                "name": name,
            },
        )

        # 4. JWT 발급
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": {
                    "email": user.email,
                    "name": user.name,
                    "is_social": user.is_social,
                    "social_type": user.social_type,
                },
            },
            status=200,
        )
