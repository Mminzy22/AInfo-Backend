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
        self.collections = self._register_collections()

    def _register_collections(self):
        """
        프로젝트에서 사용하는 주요 컬렉션을 사전 등록.

        Returns:
            dict: 컬렉션 이름을 key로, Chroma 컬렉션 인스턴스를 value로 하는 딕셔너리.
        """
        collection_names = [
            "gov24_services",
            "youth_policy_list",
            "mongddang_data",
            "pdf_sections",
        ]
        return {
            name: Chroma(
                collection_name=name,
                embedding_function=self.embedding_model,
                persist_directory=self.DB_DIR,
            )
            for name in collection_names
        }

    def search(self, query, k=5, filters=None, collection_names=None):
        """
        멀티 컬렉션 대상 유사도 검색 수행.

        Args:
            query (str): 검색 쿼리 문자열.
            k (int): 각 컬렉션별 검색 결과 수 (기본값 5).
            filters (dict, optional): 메타데이터 필터링 조건. 예: {"title": "청년"}.
            collection_names (list, optional): 검색 대상 컬렉션 이름 리스트. None이면 모든 컬렉션 사용.

        Returns:
            list: [(컬렉션 이름, Document)] 형태의 튜플 리스트. score 기준 내림차순 정렬됨.
        """
        filters = filters or {}

        if collection_names is None:
            collection_names = list(self.collections.keys())

        results = []
        for name in collection_names:
            if name not in self.collections:
                continue
            collection = self.collections[name]
            docs_with_scores = collection.similarity_search_with_score(query, k=k)
            for doc, score in docs_with_scores:
                if self._metadata_match(doc.metadata, filters):
                    results.append((name, doc, score))

        return sorted(results, key=lambda x: x[2])

    def _metadata_match(self, metadata, filters):
        """
        주어진 메타데이터가 필터 조건을 충족하는지 검사.

        Args:
            metadata (dict): 문서의 메타데이터.
            filters (dict): {"key": "value"} 형태의 조건.

        Returns:
            bool: 조건을 만족하면 True, 그렇지 않으면 False.
        """
        if not filters:
            return True
        for key, value in filters.items():
            if key not in metadata:
                return False
            if value not in str(metadata[key]):
                return False
        return True

    def format_docs(self, docs):
        """
        검색된 문서 리스트를 사용자에게 제공할 수 있는 포맷으로 변환.

        - 각 문서에서 표준화된 메타데이터(name, region, subject, detail, link)와 본문을 추출하여 마크다운 형식으로 가공.
        - 링크가 없을 경우 안내 문구로 대체.
        - score는 내부 정렬용으로만 사용되며 사용자에게 노출되지 않음.

        Args:
            docs (list): [(컬렉션 이름, Document, score)] 튜플 리스트.

        Returns:
            str: 문서들의 제목, 내용, 메타데이터를 포함한 마크다운 문자열.
        """
        formatted = []
        for name, doc, _ in docs:
            meta = doc.metadata
            content = doc.page_content.strip()

            title = meta.get("name", "제목 없음")
            region = meta.get("region", "정보 없음")
            subject = meta.get("subject", "정보 없음")
            detail = meta.get("detail", "정보 없음")
            link = meta.get("link")

            link_md = (
                f"[바로가기]({link})"
                if link
                else "해당 서비스는 URL이 제공되지 않습니다."
            )

            formatted.append(
                f"**[{title}]**\n"
                f"- 지역: {region}\n"
                f"- 지원대상: {subject}\n"
                f"- 지원내용: {detail}\n"
                f"- 링크: {link_md}\n"
                f"- 본문 요약: {content}"
            )

        return "\n\n---\n\n".join(formatted)
