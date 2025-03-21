from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from chatbot.langchain_flow.filter_utils import convert_chroma_filters
from chatbot.retriever import VectorRetriever


class RagSearchInput(BaseModel):
    """
    RAGSearchTool의 입력값 스키마 정의.

    Attributes:
        question (str): 정제된 사용자 질문
        filters (dict): 메타데이터 기반 검색 필터 (예: {"지역": "서울"})
        k (int): 검색할 문서 개수 (기본값: 5)
    """

    question: str = Field(..., description="사용자 질문(정제된 문장)")
    filters: dict = Field({}, description="Chroma 메타데이터 필터")
    k: int = Field(5, description="검색할 문서 개수")


class RAGSearchTool(BaseTool):
    """
    사용자 질문과 필터 조건을 기반으로 Chroma 벡터 DB에서 유사한 문서를 검색하는 Tool.

    - VectorRetriever를 통해 프로젝트 내 등록된 컬렉션 대상으로 검색 수행
    - 검색 결과는 텍스트 형식으로 요약되어 반환됨

    Output 형식:
        {
            "answer": "요약된 문서 콘텐츠 문자열"
        }
    """

    name: str = "rag_search_tool"
    description: str = "Chroma 벡터 DB에서 질문과 필터 조건으로 관련 문서를 검색합니다."
    args_schema: Type[BaseModel] = RagSearchInput

    def _run(self, **kwargs) -> str:
        try:
            question = kwargs["question"]
            filters = kwargs.get("filters", {})
            k = kwargs.get("k", 5)

            chroma_filter = convert_chroma_filters(filters)

            retriever = VectorRetriever()

            docs = retriever.search(
                query=question,
                filters=chroma_filter,
                k=k,
            )

            if not docs:
                return "검색된 문서가 없습니다."

            return {"answer": retriever.format_docs(docs)}

        except Exception as e:
            return f"검색 중 오류가 발생했습니다: {e}"
