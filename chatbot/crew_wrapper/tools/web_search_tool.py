from datetime import datetime
from typing import Dict, List, Optional, Type

from crewai.tools import BaseTool
from langchain_community.tools.tavily_search import TavilySearchResults
from pydantic import BaseModel

from chatbot.crew_wrapper.crews.web_crew.config.web_search_input import WebSearchInput

current_year = datetime.now().year


class SearchWebTool(BaseTool):
    name: str = "search_web_tool"
    description: str = (
        f"사용자의 질문과 조건에 따라 공공서비스 정보를 검색합니다. "
        f"이 툴은 {current_year}년 기준 데이터를 기반으로 동작합니다."
    )
    args_schema: Type[BaseModel] = WebSearchInput

    def _run(
        self,
        question: str,
        keywords: str,
        user_profile: Optional[Dict[str, str]] = None,
        collection_names: Optional[List[str]] = None,
        k: Optional[int] = 3,
    ) -> str:
        try:
            # 1. 쿼리 = 기본 질문만 사용
            query = question

            # 2. 사용자 프로필 붙이기
            if user_profile:
                profile_str = " ".join(f"{k}:{v}" for k, v in user_profile.items())
                query += f" 관련 공공서비스 {profile_str}"

            # 3. 기관 필터 붙이기
            TRUSTED_SITES = [
                "gov.kr",
                "moel.go.kr",
                "work.go.kr",
                "k-startup.go.kr",
                "youthcenter.go.kr",
                "mohw.go.kr",
                "bokjiro.go.kr",
                "mbc.go.kr",
                "seoul.go.kr",
                "gg.go.kr",
            ]

            site_filter = " OR ".join(f"site:{site}" for site in TRUSTED_SITES)
            query += f" {site_filter} 한국어로 된 공공기관 정보"

            # 4. Tavily 실행
            tavily = TavilySearchResults(k=k)
            results = tavily.run(query)

            if not results:
                raise ValueError("검색 결과가 없습니다. 검색 실패로 간주합니다.")

            # 5. 요약 정리
            summaries = []
            for item in results:
                url = item.get("url", "")
                content = (
                    item.get("content", "")
                    .strip()
                    .replace("\n", " ")
                    .replace("  ", " ")
                )
                summaries.append(f"{content} (출처: {url})")

            return "\n\n".join(summaries)

        except Exception as e:
            return f"검색 중 오류가 발생했습니다: {e}"
