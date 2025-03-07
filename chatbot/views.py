from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .retriever import VectorRetriever
from .serializers import ChatbotSerializer
from .utils import get_chatbot_response

# 서버 실행 시 벡터 개수 확인용
retriever = VectorRetriever()
print(f"🍟저장된 벡터 개수: {retriever.get_vectorstore_count()}")


class ChatbotView(APIView):
    """챗봇 API View
    - 프롬프트와 응답 처리는 prompt.py, utils.py에서 처리
    """

    def post(self, request):
        """
        - 사용자의 질문을 받아서 LLM을 실행하고 응답을 반환
        - Serializer를 이용해 유저 입력 데이터 검증
        """
        serializer = ChatbotSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {"msg": "입력 오류", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_message = serializer.validated_data["message"]

        # 챗봇 응답 처리 (utils.py에서 자동으로 RAG 수행)
        response = get_chatbot_response(user_message)

        return Response({"data": response}, status=status.HTTP_200_OK)
