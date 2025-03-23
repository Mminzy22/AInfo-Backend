from datetime import datetime
from textwrap import dedent
from typing import List

from langchain.prompts import ChatPromptTemplate
from langchain.tools.base import BaseTool


def get_news_search_prompt(tools: List[BaseTool]) -> ChatPromptTemplate:
    """
    뉴스 기반 검색 에이전트를 위한 프롬프트 템플릿을 생성합니다.

    Args:
        tools (List[BaseTool]): 에이전트가 사용할 도구 리스트

    Returns:
        ChatPromptTemplate: LangChain용 뉴스 요약 프롬프트 템플릿
    """
    current_year = datetime.now().year

    return ChatPromptTemplate.from_messages(
        [
            ("system", "사용 가능한 도구 목록: {tools_description}"),
            (
                "system",
                dedent(
                    f"""
                너는 {current_year}년 기준 최신 정책 정보를 요약해주는 챗봇이야.
                최소 3개 이상의 정보를 알려주고,
                아래 형식으로 답변을 구성해줘:

                1. 제목:
                2. 간단 요약:
                3. 출처 링크:

                뉴스 기사나 공공기관의 공식 사이트만 참고하고, 블로그나 광고성 페이지는 제외해줘.
            """
                ),
            ),
            ("placeholder", "{chat_history}"),
            ("user", "{input}"),
            ("system", "{agent_scratchpad}"),
        ]
    )
