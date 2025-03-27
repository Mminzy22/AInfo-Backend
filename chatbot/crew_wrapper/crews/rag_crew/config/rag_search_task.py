from textwrap import dedent

from crewai import Task

from chatbot.crew_wrapper.tools.rag_search_tool import RagSearchTool


def create_rag_search_task(agent, user_input: dict) -> Task:
    """
    사용자 질문과 필터를 바탕으로 RAG 검색을 수행하는 Task 생성 함수
    """
    question = user_input["original_input"]
    summary = user_input["summary"]
    profile = user_input["user_profile"]

    profile_str = "\n".join([f"- {k}: {v}" for k, v in profile.items()])

    return Task(
        description=dedent(
            f"""
        당신은 공공서비스 추천을 도와주는 AI입니다.
        사용자의 질문과 프로필 정보를 기반으로 가장 적합한 공공정책을 추천해주세요.
        만약 관련 정책 정보가 없다면 **관련 정보가 없습니다**라고 안내해 주세요.

        반드시 아래 절차를 따르세요:

        1. 사용자와의 이전 대화 요약 내용을 먼저 확인하고, 사용자 질문과 프로필에 맞는 정책 문서를 검색하세요.
        2. 검색 결과 바탕으로만 정책을 추천하세요.
        3. 절대로 툴 없이 개인적 판단이나 외부 지식을 사용하지 마세요.
        4. **사용자 질문을 우선적으로 고려**하고, 정책의 혜택과 신청 방법을 명확히 설명하세요.

        이전 대화 요약 내용:
        {summary}

        사용자 질문:
        {question}

        사용자 프로필:
        {profile_str}

        검색한 결과를 바탕으로 사용자가 신청할 수 있고 혜택이 큰 정책을 3개 이상 골라 추천해 주세요.
        정책 명칭, 설명, 신청 링크를 포함해 주세요.
        """
        ),
        expected_output="정책 이름, 설명, 추천 이유, 링크가 포함된 3개 이상의 공공서비스 정보, 만약 관련 정책 정보가 없다면 **관련 정보가 없습니다**라고 안내.",
        used_tools=True,
        agent=agent,
        tools=[RagSearchTool()],
    )
