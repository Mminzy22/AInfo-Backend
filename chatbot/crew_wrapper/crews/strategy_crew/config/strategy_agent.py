from crewai import Agent
from langchain_openai import ChatOpenAI

from chatbot.crew_wrapper.crews.strategy_crew.config.prompts import (
    STRATEGY_AGENT_PROMPT,
)


def get_strategy_agent():
    return Agent(
        role="공공서비스 수강/신청 전략 설계 전문가",
        goal="사용자의 상황에 맞춰 가장 효율적인 공공정책 신청 순서와 흐름을 설계한다.",
        backstory="정책 간 연계성, 조건 충족 시기, 우선순위를 고려해서 사용자에게 가장 현실적인 신청 로드맵을 설계해 줍니다.",
        verbose=True,
        allow_delegation=False,
        llm=ChatOpenAI(model="gpt-4o-mini", temperature=0.5, max_tokens=1024),
        system_prompt=STRATEGY_AGENT_PROMPT,
    )
