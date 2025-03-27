from textwrap import dedent

from crewai import Task


def create_compare_task(
    agent, user_input: dict, recommend_task: str, web_search_task: str
) -> Task:
    """
    RAG 또는 웹 검색을 바탕으로 후보 공공정책들을 비교하고, 사용자에게 가장 적합한 정책을 추천 Task 생성 함수
    """
    original_input = user_input["original_input"]
    summary = user_input["summary"]
    profile = user_input["user_profile"]

    profile_str = "\n".join([f"- {k}: {v}" for k, v in profile.items()])

    return Task(
        description=dedent(
            f"""
        다음은 이전 대화를 요약한 내용과 사용자의 질문, 프로필 정보입니다.
        이 정보를 바탕으로 사용자가 고려 중인 공공정책들 간의 차이를 비교 분석해 주세요.
        반드시 **사용자 질문을 우선적으로 고려**해 주세요.

        -------------------------
        이전 대화 요약 내용:
        {summary}

        사용자 질문:
        {original_input}

        사용자 프로필:
        {profile_str}

        비교 분석 대상 정책 정보:
        1. RAG 검색 결과:
        {recommend_task}

        2. WEB 검색 결과:
        {web_search_task}
        -------------------------

        요청사항:
        - 각 정책의 주요 항목(지원 대상, 조건, 금액, 신청 방법 등)을 항목별로 비교해 주세요.
        - 단순 요약이 아니라, **정책 간 차이점**을 명확하게 드러내 주세요.
        - 사용자의 상황(나이, 관심사, 지역 등)에 더 적합한 정책이 있다면 그 이유와 함께 추천해 주세요.
        - 어려운 용어는 풀어서 설명하고, **사용자가 쉽게 판단할 수 있도록** 도와주세요.
        """
        ),
        expected_output=dedent(
            """
        정책별 비교표, 핵심 차이점 요약, 추천 사유, 링크를 포함한 분석 결과를 아래 형식으로 작성해 주세요.
        만약 관련 정책 정보가 없다면 관련 정보가 없다고 안내해 주세요.

        ### 📊 정책 비교 분석

        **정책 1 요약:**
        - 서비스명:
        - 지원 대상:
        - 지원 내용:
        - 신청 방법:
        - 신청 링크:

        **정책 2 요약:**
        - 서비스명:
        - 지원 대상:
        - 지원 내용:
        - 신청 방법:
        - 신청 링크:

        ...

        ### ✅ 비교 분석 요약

        - 핵심 차이점 요약:
        예: 정책 1은 창업 지원, 정책 2는 취업 준비 지원
        - 사용자에게 더 적합한 정책: **정책 2**
        - 추천 사유:
        예: 사용자의 관심사와 지원 대상 조건에 가장 잘 부합하며, 즉시 신청 가능
        """
        ),
        agent=agent,
    )
