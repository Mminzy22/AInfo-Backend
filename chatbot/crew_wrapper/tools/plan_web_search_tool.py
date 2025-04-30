# chatbot/crew_wrapper/tools/plan_web_search_tool.py

from crewai.tools import tool
from langchain_tavily import TavilySearch


@tool("plan_web_search_tool")
def plan_web_search_tool(query: str) -> str:
    """
    공공서비스 신청 전략 수립 과정에서 정보가 부족할 때 추가 정보를 신뢰도 높은 도메인 (예: gov.kr, moel.go.kr 등)에서 검색하는 Tavily 검색 도구입니다.

    Args:
        query (str): 특정 공공서비스명이 포함된 검색에 사용할 쿼리 문자열.

    Returns:
        str: 검색 결과 (제목, 서비스 실행 지역, 지원대상, 지원내용, 서비스 관련 링크, 전략수립에 필요한 추가 정보 포함)
    """
    # TavilySearch 인스턴스 생성
    tavily_search = TavilySearch(
        max_results=3,
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

    result = tavily_search.invoke({"query": query})
    return result
