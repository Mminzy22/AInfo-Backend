from crewai.tools import tool

from chatbot.retriever import VectorRetriever


@tool("vector_meta_search_tool")
def vector_meta_search_tool(service_name: str) -> str:
    """
    특정 공공서비스명(service_name)을 메타데이터 필터링을 이용해 벡터 검색하는 CrewAI Tool.

    Args:
        service_name (str): 검색에 사용할 공식적인 공공서비스명 (메타데이터의 name 필드 기준이므로 정확한 서비스명 또는 공공서비스명에 포함된 특정 키워드만 입력해야 함).

    Returns:
        str: 검색된 서비스 정보를 마크다운 형식으로 정리한 문자열.
    """
    retriever = VectorRetriever()

    # 'name' 메타데이터 필드를 기준으로 필터링 추가
    results = retriever.search(query=service_name, filters={"name": service_name})

    return retriever.format_docs(results)
