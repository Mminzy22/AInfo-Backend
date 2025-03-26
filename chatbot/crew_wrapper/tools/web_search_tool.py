from datetime import datetime
from typing import Dict, List, Optional, Type

from crewai.tools import BaseTool
from langchain.tools.tavily_search import TavilySearchResults
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
        keywords: List[str],
        collection_names: Optional[List[str]] = None,
        k: Optional[int] = 5,
        filters: Optional[Dict[str, str]] = None,
    ) -> str:
        try:
            tool = TavilySearchResults(k=k)
            results = tool.run(question)

            if not results:
                return "검색 결과가 없습니다."

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
