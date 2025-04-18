from textwrap import dedent

from crewai import Task

from chatbot.crew_wrapper.tools.strategy_web_tool import StrategyWebTool


def create_strategy_task(
    agent,
    user_input: dict,
    recommend_task: str,
    web_search_task: str,
    compare_task: str,
) -> Task:
    """
    비교 분석 결과를 바탕으로 사용자에게 정책 수강/신청 전략을 제시하는 Task 생성 함수
    """
    original_input = user_input["original_input"]
    summary = user_input["summary"]
    profile = user_input["user_profile"]

    profile_str = "\n".join([f"- {k}: {v}" for k, v in profile.items()])

    return Task(
        description=dedent(
            f"""
        다음은 이전 대화를 요약한 내용과 사용자의 질문, 프로필 정보, 그리고 관련 정책 문서입니다.
        이 정보를 바탕으로 사용자가 어떤 순서로 어떤 정책을 신청하거나 수강해야 가장 효율적인지 전략을 짜 주세요.
        반드시 **사용자 질문을 우선적으로 고려**해 주세요.

        -------------------------
        이전 대화 요약 내용:
        {summary}

        사용자 질문:
        {original_input}

        사용자 프로필:
        {profile_str}

        추천 또는 검색된 정책 리스트:
        1. RAG 검색 결과:
        {recommend_task}

        2. WEB 검색 결과:
        {web_search_task}

        정책 간 비교 분석 결과:
        {compare_task}
        -------------------------

        요청사항:
        - 정책 간 우선순위가 분명하다면 그 순서를 제시하고, 그 이유를 설명해 주세요.
        - 만약 정책 간 우선순위가 명확하지 않다면, 각 정책별로 실행 순서나 신청 방법을 상세하게 안내해 주세요.
        - 사용자가 지금 당장 할 수 있는 행동부터 설명해 주세요.
        - 사용자 입장에서 실천 가능한 구체적인 전략이어야 하며, 친절하고 쉽게 설명해 주세요.
        """
        ),
        expected_output=dedent(
            """
        아래 형식을 따라 사용자가 바로 실천할 수 있는 정책 신청 전략을 작성해 주세요.
        만약 관련 정책 정보가 없다면 관련 정보가 없다고 안내해 주세요.

        요구사항:
        - 정책 간 비교 분석 결과에서 **사용자에게 적합하다고 판단된 정책**을 중심으로 전략을 수립
        - 정책 간 우선순위가 있을 경우 **1단계 → 2단계 → ...** 순서로 안내하고, 각 단계마다 이유를 설명
        - 정책 간 우선순위가 없다면, 각 정책별로 **신청 방법이나 실행 순서**를 구체적으로 안내
        - 너무 어려운 전문 용어는 피하고, **친절하고 쉬운 말**로 작성
        - **정책 이름과 링크가 있다면 포함**, 없으면 생략 가능

        출력 예시 (정책 간 우선순위가 없는 경우):

        ### 🗺️ 맞춤형 정책 활용 전략 안내

        **🔹 취업날개 면접정장 대여 서비스**
        - 먼저 서울청년포털에 회원가입하세요.
        - 이후 [서비스 신청 페이지](https://example.com/1)에 접속해 쿠폰을 신청합니다.
        - 문자를 받은 후 제휴 미용실에 예약하여 정장을 대여할 수 있어요.

        **🔹 K-패스 교통비 지원**
        - 고용노동부 청년정책 홈페이지에 로그인합니다.
        - 신청서를 작성한 뒤 본인 인증을 완료하면 자동으로 교통비가 지원됩니다.
        - [신청 바로가기](https://example.com/2)

        출력 예시 (정책 간 우선순위가 있는 경우):

        **1단계. 청년 면접수당 신청하기**
        - 면접을 앞두고 있다면 지금 바로 신청 가능한 정책입니다.
        - 혜택을 빠르게 받을 수 있어 가장 먼저 진행하는 것이 좋습니다.
        - 👉 [신청 링크](https://example.com/3)

        ...

        이와 같은 형식으로 사용자가 지금 바로 실천 가능한 전략을 구성해 주세요.
        """
        ),
        used_tools=True,
        agent=agent,
        tools=[StrategyWebTool()],
    )
