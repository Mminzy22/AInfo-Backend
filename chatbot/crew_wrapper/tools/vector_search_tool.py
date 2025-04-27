from chatbot.retriever import VectorRetriever
from crewai.tools import tool

@tool("vector_search_tool")
def vector_search_tool(keyword: str, filters: dict=None) -> str:
    """
    키워드를 기반으로 벡터 검색을 수행하는 툴.

    Args:
        keywords (str): 검색에 사용할 키워드.
        filters (dict, optional): 메타데이터 필터링 조건. 예: {"name": "청년"}.

    Returns:
        str: 검색 결과를 마크다운 형식으로 포맷한 문자열.

        형식 예시:
        **[공공서비스명]**
        - 지역: ...
        - 지원대상: ...
        - 지원내용: ...
        - 링크: ...
        - 본문 요약: ...
    """
    retriever = VectorRetriever()
    results = retriever.search(
        query=keyword,
        filters=filters
    )
    return retriever.format_docs(results)
