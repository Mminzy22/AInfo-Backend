from datetime import datetime
from textwrap import dedent

from crewai import Task

from chatbot.crew_wrapper.tools.web_search_tool import SearchWebTool


def create_web_search_task(agent, user_input: dict) -> Task:
    """
    사용자 질문과 프로필 정보를 바탕으로 WEB 검색을 수행하는 Task 생성 함수
    """
    original_input = user_input["original_input"]
    keywords = user_input["keywords"]
    profile = user_input["user_profile"]

    current_year = datetime.now().year
    profile_str = "\n".join([f"- {k}: {v}" for k, v in profile.items()])

    return Task(
        description=dedent(
            f"""
        당신은 공공서비스 추천을 도와주는 AI입니다.
        사용자의 질문과 프로필 정보를 기반으로 가장 적합한 공공정책을 추천해주세요.

        반드시 아래 절차를 따르세요:

        1. 반드시 search_web_tool을 사용하세요. ({current_year}년 기준의 최신 데이터를 기반으로 검색합니다)
        2. 사용자 질문을 우선적으로 고려하고, 정책의 혜택과 신청 방법을 명확히 설명하세요.
        3. 결과가 없거나 부정확해도 직접 작성하지 마세요.
        4. 검색 결과만 바탕으로 요약 정보를 제공하세요.
        5. 불필요한 개인적 해석은 하지 마세요.
        6. 광고성 정보는 제외하세요.

        사용자 질문:
        {original_input}

        사용자 프로필:
        {profile_str}

        검색한 결과를 바탕으로 사용자가 신청할 수 있고 혜택이 큰 정책을 3개 이상 골라 추천해 주세요.
        제목, 웹 요약 정보, 링크를 포함해 주세요.
        """
        ),
        expected_output="정책 이름, 설명, 추천 이유, 링크가 포함된 3개 이상의 공공서비스 정보",
        agent=agent,
        tools=[SearchWebTool()],
        tool_input={
            "question": original_input,
            "keywords": keywords,
            "filters": profile,
        },
        output_key="recommendation",
    )
