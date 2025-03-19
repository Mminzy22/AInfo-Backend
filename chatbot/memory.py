import redis
from django.conf import settings
from langchain.memory import ConversationSummaryBufferMemory
from langchain_community.chat_message_histories import RedisChatMessageHistory


class ChatHistoryManager:
    """
    사용자의 챗봅 대화 기록을 Redis에 저장하고 관리하는 클래스

    Redis를 이용해서 사용자의 대화를 기록 저장하고,
    LangChain의 `ConversationSummaryBufferMemory`를 통해 200 token 이상의 대화는 요약해서 prompt에 전달해서 사용합니다.
    대화가 길어져도 성능이나 경제적으로 효율적인 방식으로 과거의 대화 내용을 반영해서 답변을 얻을 수 있게 됩니다.

    주요기능:
        - Redis를 활용한 사용자별 대화 기록 저장
        - `ConversationSummaryBufferMemory`를 이용한 대화 요약 및 멀티턴 대화 관리
        - Redis에 저장된 대화 기록을 삭제하는 기능
    Args:
        user_id = 사용자의 id
        model = 길어진 대화를 요약하는데 사용하는 LLM 모델
        max_token_limit : 대화 요약을 위한 최대 토큰 제한 (default = 200)

    Methods:
        get_memory_manager(): 사용자의 대화를 관리할 `ConversationSummaryBufferMemory` 객체 반환
        clear_history(): 사용자의 대화 기록을 Redis에서 삭제
    """

    REDIS_DB = 1

    def __init__(self, user_id, model, max_token_limit=200):
        """ChatHistoryManager 클래스 생성자"""
        self.user_id = str(user_id)
        self.model = model
        self.max_token_limit = max_token_limit
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=self.REDIS_DB,
            decode_responses=True,
        )

        self.chat_history = RedisChatMessageHistory(
            session_id=self.user_id,
            url=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{self.REDIS_DB}",
        )

    def get_memory_manager(self):
        """사용자 대화 기록을 관리할 `ConversationSummaryBufferMemory 인스턴스 생성 매서드"""
        return ConversationSummaryBufferMemory(
            llm=self.model,
            chat_memory=self.chat_history,  # Redis에서 관리하는 대화 기록 객체
            max_token_limit=self.max_token_limit,
            return_messages=True,  # 전체 대화 메시지 반환 여부
            memory_key="chat_history",  # 저장된 대화 기록의 key 값
        )

    def clear_history(self):
        """Redis에서 대화기록 삭제 매서드"""
        self.chat_history.clear()
