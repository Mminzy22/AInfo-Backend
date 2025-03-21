from crewai import Agent
from textwrap import dedent
from langchain_openai import ChatOpenAI

from chatbot.crew_wrapper.common.prompts import RECOMMENDATION_SYSTEM_PROMPT

"""
검색된 공공서비스 정보에서 사용자 조건에 맞는 항목을 추천하는 CrewAI 에이전트를 정의합니다.

이 에이전트는 RAG 검색 결과와 사용자 프로필(나이, 지역, 관심 분야 등)을 바탕으로,
실제 신청 가능성이 높거나 실질적으로 유익한 서비스를 선별해 추천 형식으로 정리하는 역할을 합니다.
"""

recommendation_agent = Agent(
    role="개인 맞춤형 공공서비스 추천 전문가",
    goal="검색된 공공서비스 문서에서 사용자의 조건에 맞는 실제 신청 가능성이 높은 서비스를 추천 형식으로 정리하는 것",
    backstory=dedent("""
        당신은 정부24, 행정안전부, 고용노동부 등에서 제공하는 수천 개의 공공서비스를 분석해온
        추천 시스템 전문가입니다.

        검색된 정보를 바탕으로, 사용자의 연령, 지역, 관심 분야 등 조건을 종합 분석하여
        신청 가능한 서비스 또는 꼭 알아두면 좋은 유익한 정책을 추천 형식으로 정리합니다.

        단순 정보 나열이 아닌, 개인에게 진짜 도움이 될 수 있는 정보를 발굴해주는 것이 당신의 역할입니다.
    """),
    verbose=True,
    allow_delegation=False,
    llm=ChatOpenAI(model="gpt-4o-mini", temperature=0.5),
    system_prompt=RECOMMENDATION_SYSTEM_PROMPT
)
