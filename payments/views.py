# views.py
import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Payment


class PayVerify(APIView):
    """
    Description: 결제 검증요청을 처리하는 함수

    - 요청과 함께받은 결제id 를 이용해 기존 webhook으로 인해 저장된 DB 에서 맞는 결제건을 찾음
    - 해당 결제건의 상태가 완료(Paid) 상태라면 해당 유저 크레딧 100 증가 후 저장
    """

    def post(self, request):
        user = request.user
        payment_id = request.data.get("payment_id")

        payment = Payment.objects.filter(payment_id=payment_id).first()

        if not payment:
            return Response(
                {"error": "Invalid payment_id"}, status=status.HTTP_400_BAD_REQUEST
            )

        if payment.status == "Paid":
            payment.user = user
            payment.save()
            user.credit += 100
            user.save()

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
    return JsonResponse(
        {
            "message": "DB update success",
        }
    )
