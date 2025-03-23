from datetime import datetime

from langchain.agents import tool
from langchain_community.tools.tavily_search import TavilySearchResults

current_year = datetime.now().year


@tool
def news_search_tool(query: str) -> str:
    """
    공공 뉴스 도메인에 한정된 Tavily 검색 수행 툴.

    Args:
        query (str): 사용자 검색어

    Returns:
        str: Tavily API를 통해 수집된 뉴스 요약 결과

    최신 뉴스 기반 검색을 수행합니다.
    공공정책 관련 정보를 검색합니다.
    Tavily API를 이용하며, 신뢰할 수 있는 공식 뉴스 사이트만 대상으로 합니다.
    """
    modified_query = f"{query} site:korea.kr OR site:yna.co.kr OR site:news.kbs.co.kr"
    return TavilySearchResults(k=5)._run(modified_query)


news_search_tool.__doc__ += (
    f"\n\n이 툴은 {current_year}년 기준 데이터를 기반으로 검색합니다."
)
