from textwrap import dedent

from crewai import Agent
from langchain_openai import ChatOpenAI

from chatbot.crew_wrapper.common.prompts import RAG_SEARCH_SYSTEM_PROMPT

"""
공공서비스 추천 시스템에서 RAG 기반 검색을 수행하는 에이전트를 정의합니다.

이 에이전트는 정책 및 서비스 정보를 기반으로,
사용자 프로필과 질문에 따라 신청 가능하거나 유익한 정보를 분석하고 요약하는 역할을 합니다.
"""

rag_search_agent = Agent(
    role="공공서비스 정보 검색 및 분석 전문가",
    goal="다양한 공공서비스 문서에서 신청 가능하거나 유익한 정보를 정확히 찾아주는 것",
    backstory=dedent(
        """
        당신은 정부24, 고용24, 행정안전부 등에서 제공하는 다양한 공공서비스 데이터를 빠르게 분석할 수 있는 전문가입니다.
        사용자의 질문과 프로필 정보를 바탕으로, 벡터 DB에 저장된 공공서비스 문서 중 신청 자격에 부합하거나
        실질적인 도움이 되는 정보를 찾아냅니다.
    """
    ),
    verbose=True,
    allow_delegation=False,
    llm=ChatOpenAI(model="gpt-4o-mini", temperature=0.3),
    system_prompt=RAG_SEARCH_SYSTEM_PROMPT,
)
