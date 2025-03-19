import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render
from django.utils.http import urlsafe_base64_decode
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import CurrentStatus, EducationLevel, Interest, SubRegion
from .serializers import (
    CurrentStatusSerializer,
    EducationLevelSerializer,
    InterestSerializer,
    ResetPasswordSerializer,
    SignupSerializer,
    SubRegionSerializer,
    UserSerializer,
)
from .tasks import send_reset_pw_email, send_verify_email
from .tokens import token_for_verify_mail

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
        - 기존 메일발송 로직 tasks.py 로 이동 -> Celery 로 비동기처리하기 위함
        """
        user = serializer.save()

        current_site = get_current_site(self.request)
        domain = current_site.domain
        send_verify_email.delay(user.id, user.email, domain)

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


class ActivateEmailView(APIView):
    """
    Description: 메일로보낸 인증링크를 통해 들어온요청 을 처리하는 클래스

    - uid, token 과같이 보낸 인증메일을 통해 판별한후 email_verified 를 True 로 변경
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request, uid, token):
        try:
            # uid 디코딩
            uid_decoded = urlsafe_base64_decode(uid).decode()
            user = User.objects.get(pk=uid_decoded)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        # 토큰 확인
        if user and token_for_verify_mail.check_token(user, token):
            user.email_verified = True
            user.save()
            return Response(
                {"message": "이메일 인증이 완료되었습니다."}, status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"error": "잘못된 인증 링크입니다."}, status=status.HTTP_400_BAD_REQUEST
            )


class ResetPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            user = User.objects.filter(email=email).first()

            current_site = get_current_site(request)
            domain = current_site.domain

            if user:
                send_reset_pw_email.delay(user.id, email, domain)
                return Response(
                    {"message": "인증링크를 전송했습니다. 이메일을 확인해주세요"},
                    status=status.HTTP_200_OK,
                )

        return Response(
            {"message": "해당 계정은 존재하지 않습니다"},
            status=status.HTTP_404_NOT_FOUND,
        )


class ResetPasswordRenderView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, uid, token):
        try:
            # uid 디코딩
            uid_decoded = urlsafe_base64_decode(uid).decode()
            user = User.objects.get(pk=uid_decoded)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user and token_for_verify_mail.check_token(user, token):
            return render(
                request, "account/password_reset.html", {"uid": uid, "token": token}
            )

    def post(self, request, uid, token):
        try:
            # uid 디코딩
            uid_decoded = urlsafe_base64_decode(uid).decode()
            user = User.objects.get(pk=uid_decoded)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user and token_for_verify_mail.check_token(user, token):
            new_password = request.data.get("new_password")
            confirm_password = request.data.get("confirm_password")

            if new_password != confirm_password:
                return Response(
                    {"message": "비밀번호와 비밀번호 확인이 일치하지 않습니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user.set_password(new_password)
            user.save()
            return Response(
                {"message": "비밀번호가 성공적으로 변경되었습니다."},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"message": "유효하지 않은 토큰입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
