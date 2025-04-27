# chatbot/crew_wrapper/tools/web_search_tool.py

from crewai.tools import tool
from langchain_tavily import TavilySearch

@tool("web_search_tool")
def web_search_tool(original_input: str) -> str:
    """
    신뢰도 높은 도메인 (예: gov.kr, moel.go.kr 등)에서 공공서비스 정보를 검색하는 Tavily 검색 도구입니다.
    
    Args:
        original_input (str): 검색에 사용할 쿼리 문자열.

    Returns:
        str: 검색 결과 리스트 (제목, 상세내용, 링크 포함)
    """
    # TavilySearch 인스턴스 생성
    tavily_search = TavilySearch(
        max_results=5,
        topic="general",
        include_answer=True,
        include_raw_content=True,
        search_depth="advanced",
        time_range="year",
        include_domains=[
            "gov.kr",
            "moel.go.kr",
            "work24.go.kr",
            "k-startup.go.kr",
            "youthcenter.go.kr",
            "mohw.go.kr",
            "bokjiro.go.kr",
            "seoul.go.kr",
            "gg.go.kr",
        ],
    )

    result = tavily_search.invoke({"query": original_input})
    return result
