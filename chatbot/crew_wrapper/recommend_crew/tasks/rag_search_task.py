from textwrap import dedent

from crewai import Task

from chatbot.crew_wrapper.recommend_crew.tools.rag_search_tool import RAGSearchTool


def create_rag_search_task(agent, user_input: dict) -> Task:
    """
    사용자 질문과 프로필 조건을 기반으로 RAG 벡터 검색을 수행하는 CrewAI Task를 생성합니다.

    Args:
        agent (Agent): 검색을 수행할 에이전트 인스턴스
        user_input (dict): 사용자 입력 딕셔너리 (예: {"question": "...", "filters": {...}})

    Returns:
        Task: 검색 Task 객체. 검색 결과는 다음 Task로 context로 전달될 수 있습니다.
    """

    question = user_input["question"]
    filters = user_input.get("filters", {})

    return Task(
        description=dedent(
            f"""
            다음 사용자 질문에 대해 공공서비스 문서 중,
            사용자의 조건(프로필)에 맞는 정보를 검색해 주세요.

            질문: "{question}"

            사용자 프로필 정보:
            {filters}

            검색 대상 문서에는 정부24, 행정안전부, 고용24 등의 공공서비스 안내가 포함되어 있습니다.
            사용자가 실제로 신청할 수 있는 서비스, 또는 실질적으로 도움이 될 수 있는 정보를 중심으로 추출해 주세요.

            다음 기준을 우선 고려하세요:
            - 연령, 지역, 관심 분야 등 사용자 조건에 부합하는 정보인지
            - 서비스의 신청 자격이나 지원 내용이 명확히 나와 있는지

            배경 설명 없이 핵심 정보만 정리해 주세요.
        """
        ),
        expected_output=dedent(
            """
            - 관련 공공서비스명
            - 간단한 서비스 요약
            - 신청 자격 요약 (있을 경우)

            위 내용을 리스트 형태 또는 짧은 단락 형식으로 정리해 주세요.
        """
        ),
        agent=agent,
        tools=[RAGSearchTool()],
    )
