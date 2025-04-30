# chatbot/crew_wrapper/tools/vector_search_tool.py

from crewai.tools import tool

from chatbot.retriever import VectorRetriever


@tool("vector_search_tool")
def vector_search_tool(keyword: str) -> str:
    """
    name, region 정보 없어서 keywords만 사용하여 벡터 검색을 수행하는 툴.

    Args:
        keywords (str): 검색에 사용할 키워드.

    Returns:
        str: 검색 결과를 마크다운 형식으로 포맷한 문자열.
             결과가 없으면 '검색 결과가 없습니다.'를 반환합니다.
    """
    try:
        retriever = VectorRetriever()

        results = retriever.search(query=keyword)

        if not results:
            return "검색 결과가 없습니다."

        return retriever.format_docs(results)
    except Exception as e:
        return f"검색 도중 오류 발생: {str(e)}"
