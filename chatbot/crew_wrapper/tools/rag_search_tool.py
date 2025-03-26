from typing import Dict, List, Optional, Type

from crewai.tools import BaseTool
from pydantic import BaseModel

from chatbot.crew_wrapper.crews.rag_crew.config.rag_search_input import PolicyQueryInput
from chatbot.retriever import VectorRetriever


class RagSearchTool(BaseTool):
    name: str = "rag_search_tool"
    description: str = "Chroma 벡터 DB에서 질문과 필터 조건으로 관련 문서를 검색합니다."
    args_schema: Type[BaseModel] = PolicyQueryInput

    def _run(
        self,
        question: str,
        keywords: str,
        collection_names: Optional[List[str]] = None,
        k: Optional[int] = 5,
        filters: Optional[Dict[str, str]] = None,
    ) -> str:

        try:
            query = "".join(keywords)

            # Chroma 필터로 변환 (이거 지웅님이 할 꺼)
            # chroma_filter = convert_chroma_filters(filters)

            chroma_filter = {}

            retriever = VectorRetriever()

            docs = retriever.search(
                query=query,
                filters=chroma_filter,
                collection_names=collection_names,
                k=k,
            )

            if not docs:
                return "검색된 문서가 없습니다."

            return retriever.format_docs(docs)

        except Exception as e:
            return f"검색 중 오류가 발생했습니다: {e}"
