from crewai import Task
from textwrap import dedent

def create_recommendation_task(agent, user_input: dict, rag_task: Task) -> Task:
    """
    사용자 프로필과 RAG 검색 결과를 바탕으로 추천 메시지를 생성하는 Task를 반환합니다.

    Args:
        agent (Agent): 추천 메시지를 작성할 에이전트 인스턴스
        user_input (dict): 사용자 질문 및 필터 조건 (예: {"question": "...", "filters": {...}})
        rag_task (Task): 이전에 실행된 RAG 검색 Task 객체 (context로 사용됨)

    Returns:
        Task: CrewAI에서 실행 가능한 추천 메시지 생성 Task
    """

    filters = user_input.get("filters", {})

    return Task(
        description=dedent(f"""
            다음은 사용자의 질문과 프로필 조건을 기반으로 검색된 공공서비스 정보입니다.

            사용자에게 **신청 가능하거나 실질적으로 도움이 될 수 있는** 서비스를 선별하여,
            다음 형식에 맞는 **개인 맞춤형 추천 메시지**를 작성해 주세요.

            사용자 프로필:
            {filters}

            검색 결과:
            {{rag_task}}

            작성 시 유의사항:
            - 너무 일반적인 설명은 제외하고, 실제 신청 자격 여부를 중심으로 작성
            - 사용자의 조건과 서비스가 어떻게 연결되는지 명확히 설명
            - 말투는 친절하고 현실적인 정보 전달 중심
        """),
        expected_output=dedent("""
            다음 형식을 따르세요:

            - 사업명: (공공서비스 또는 정책 이름)
            - 추천 이유: (사용자의 조건과 어떻게 부합하는지 설명)
            - 신청 대상: (연령, 지역, 직업 등 신청 조건 명시)
        """),
        agent=agent,
        context=[rag_task]
    )
