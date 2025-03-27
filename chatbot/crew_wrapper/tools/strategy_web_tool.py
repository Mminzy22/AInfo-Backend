from datetime import datetime
from typing import Dict, List, Optional, Type

from crewai.tools import BaseTool
from langchain_community.tools.tavily_search import TavilySearchResults
from pydantic import BaseModel

from chatbot.crew_wrapper.crews.strategy_crew.config.strategy_web_input import (
    StrategyWebInput,
)

current_year = datetime.now().year


class StrategyWebTool(BaseTool):
    name: str = "Strategy_web_tool"
    description: str = (
        f"사용자의 질문과 조건에 따라 공공서비스의 전략 및 신청 순서 또는 우선 순위를 검색합니다."
        f"이 툴은 {current_year}년 기준 데이터를 기반으로 동작합니다."
    )
    args_schema: Type[BaseModel] = StrategyWebInput

    def _run(
        self,
        question: str,
        keywords: str,
        user_profile: Optional[Dict[str, str]] = None,
        collection_names: Optional[List[str]] = None,
        k: Optional[int] = 3,
    ) -> str:
        try:
            # 1. 기본 쿼리 생성
            query = keywords if keywords else question
            if user_profile:
                profile_str = " ".join(f"{k}:{v}" for k, v in user_profile.items())
                query += f" 전략적 공공서비스 신청 순서 {profile_str}"

            # 2. 정부기관 사이트 필터 추가 (1차 시도)
            site_filter = (
                "site:gov.kr OR site:moel.go.kr OR site:work.go.kr OR "
                "site:k-startup.go.kr OR site:youthcenter.go.kr OR "
                "site:mohw.go.kr OR site:bokjiro.go.kr OR site:seoul.go.kr"
            )
            trusted_query = f"{query} {site_filter}"

            # 3. Tavily로 검색 (1차)
            tavily = TavilySearchResults(k=k)
            results = tavily.run(trusted_query)

            # 4. 결과가 없거나 부실한 경우 → 전체 검색으로 fallback
            def is_result_meaningless(results):
                if not results or not isinstance(results, list):
                    return True
                total_content = " ".join([r.get("content", "") for r in results])
                return (
                    len(total_content.strip()) < 100
                    or "관련 정보가 없습니다" in total_content
                    or "정보를 찾을 수 없습니다" in total_content
                )

            if is_result_meaningless(results):
                print("정부기관 결과 부족 → 전체 웹 검색으로 확장")
                results = tavily.run(query)

            # 5. 여전히 없다면 종료
            if not results:
                return "관련 정보가 없습니다."

            # 6. 결과 정리
            summaries = []
            for i, item in enumerate(results):
                url = item.get("url", "")
                content = (
                    item.get("content", "")
                    .strip()
                    .replace("\n", " ")
                    .replace("  ", " ")
                )
                summaries.append(f"{i+1}. {content} (출처: {url})")

            return "\n\n".join(summaries)

        except Exception as e:
            return f"검색 중 오류가 발생했습니다: {e}"
