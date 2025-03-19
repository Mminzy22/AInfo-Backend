from datetime import datetime

from langchain.tools import Tool
from langchain_community.tools.tavily_search import TavilySearchResults

current_year = datetime.now().year


def search_news_only(query: str) -> str:
    """
    공공 뉴스 도메인에 한정된 Tavily 검색 수행 함수.

    Args:
        query (str): 사용자 검색어

    Returns:
        str: Tavily API를 통해 수집된 뉴스 요약 결과
    """
    modified_query = f"{query} site:korea.kr OR site:yna.co.kr OR site:news.kbs.co.kr"
    return TavilySearchResults(k=5)._run(modified_query)


news_search_tool = Tool(
    name="tavily_news_search_tool",
    func=search_news_only,
    description=f"""{current_year}년 기준 뉴스 기반 검색을 수행합니다.
공공정책 관련 정보를 검색합니다.
Tavily API를 이용하며, 신뢰할 수 있는 공식 뉴스 사이트만 대상으로 합니다.""",
)
