# views.py
import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class PayVerify(APIView):

    def post(self, request):
        user = request.user
        payment_id = request.data.get("payment_id")
        print("----" * 18)
        print(f"user : {user}")
        print(f"payment_id : {payment_id}")
        print("----" * 18)
        print(f"request : {request}")

        return Response(
            {"message": "결제 상태 업데이트 완료"}, status=status.HTTP_200_OK
        )


@csrf_exempt  # 웹훅 요청은 외부에서 오기 때문에 CSRF 검증을 비활성화
def payment_webhook(request):  # 추후에 비동기처리 고려
    if request.method == "POST":  # 웹훅 요청은 보통 POST 방식

        try:
            data = json.loads(request.body)  # 요청의 JSON 데이터를 파싱
            payment_status = data.get("status")  # 결제 상태 (예: success, failed)
            payment_id = data.get("payment_id")  # 결제 ID

            print("----" * 18)
            print(f"request : {request}")
            print("----" * 18)
            print(f"request.data : {request.data}")
            print(f"request.type : {request.type}")
            print(f"request.timestamp : {request.timestamp}")
            print("----" * 18)
            print(f"request.payment_id : {request.payment_id}")
            print(f"request.tx_id : {request.tx_id}")
            print(f"request.status : {request.status}")
            header = request.headers
            print(f"header : {header}")

            # 결제가 성공했을 경우
            if payment_status == "success":
                print(f"✅ 결제 성공! ID: {payment_id}")
                # TODO: 결제 정보를 데이터베이스에 저장하는 로직 추가

            return JsonResponse({"message": "Webhook received"}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

    return JsonResponse({"error": "Invalid request"}, status=400)
