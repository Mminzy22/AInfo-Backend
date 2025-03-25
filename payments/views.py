# views.py
import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Payment
import hashlib
import hmac
from django.conf import settings


class PayVerify(APIView):

    def post(self, request):
        user = request.user
        payment_id = request.data.get("payment_id")

        payment = Payment.objects.filter(payment_id=payment_id).first()
        
        if not payment:
            return Response({"error": "Invalid payment_id"}, status=status.HTTP_400_BAD_REQUEST)
        
        payment.user = user
        payment.save()
        
        # 유저 DB 에서 크레딧 증가시키는 로직 추가예정

        return Response(
            {"message": "결제 상태 업데이트 완료"}, status=status.HTTP_200_OK
        )


@csrf_exempt  # 웹훅 요청은 외부에서 오기 때문에 CSRF 검증을 비활성화
def payment_webhook(request):
    """
    Description: 결제를 진행함에 따라 Portone 에서 보내는 Webhook 을 처리하기 위한 함수
    
    - Webhook 으로 오는 내용중 결제ID 와 결제상태 를 내 DB 에 저장
    """
    if request.method == "POST":
        # 요청 본문 파싱
        data = json.loads(request.body)  
        payment_status = data.get("status")  # 결제 상태 (예: Paid, Ready)
        payment_id = data.get("payment_id")  # 결제 ID
        
        # 결제 정보 DB 저장
        payment, created = Payment.objects.update_or_create(
            payment_id=payment_id,  
            defaults={"status": payment_status},
        )
    return JsonResponse({
        "message": "DB update success",
        })
