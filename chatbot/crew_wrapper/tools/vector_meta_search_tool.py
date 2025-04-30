from crewai.tools import tool
from chatbot.retriever import VectorRetriever


@tool("vector_meta_search_tool")
def vector_meta_search_tool(keyword: str, name: str = None, region: str = None) -> str:
    """
    name, region 정보가 주어졌을 경우, 주어진 keywords와 name, region 기반으로 벡터 검색을 수행하는 툴.

    Args:
        keywords (str): 검색에 사용할 키워드.
        name (str): 검색에 사용할 메타데이터 필터링 조건 중 서비스명(선택).
        region (str): 검색에 사용할 메타데이터 필터링 조건 중 서비스 지역명(선택).

    Returns:
        str: 검색 결과를 마크다운 형식으로 포맷한 문자열.
             결과가 없으면 '검색 결과가 없습니다.'를 반환합니다.
    """
    try:
        retriever = VectorRetriever()

        if name:
            name = name[:2]
        if region:
            region = region[:2]

        # 유효한 필터만 구성 (None 값 제거)
        filters = {k: v for k, v in {"name": name, "region": region}.items() if v}

        results = retriever.search(query=keyword, filters=filters)

        if not results:
            return "검색 결과가 없습니다."

        return retriever.format_docs(results)
    except Exception as e:
        return f"검색 도중 오류 발생: {str(e)}"
    