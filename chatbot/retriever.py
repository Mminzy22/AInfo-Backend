from django.conf import settings
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings


class VectorRetriever:
    """
    멀티 컬렉션 벡터 검색을 위한 싱글톤 클래스.

    - 여러 Chroma 컬렉션을 사전에 등록하고,
      멀티 컬렉션 유사도 검색 및 메타데이터 필터링을 지원.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VectorRetriever, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """
        인스턴스 초기화 메서드.

        - OpenAI 임베딩 모델 로드
        - 자주 사용하는 Chroma 컬렉션들을 등록
        """
        self.DB_DIR = settings.CHROMA_DB_DIR
        self.embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")
