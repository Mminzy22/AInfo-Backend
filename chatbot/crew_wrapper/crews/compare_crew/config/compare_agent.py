from crewai import Agent
from langchain_openai import ChatOpenAI

from chatbot.crew_wrapper.crews.compare_crew.config.prompts import COMPARE_AGENT_PROMPT


def get_compare_agent():
    return Agent(
        role="공공정책 비교 분석 전문가",
        goal="사용자의 질문과 관심사, 프로필을 기반으로 후보 정책을 비교하고 최적의 정책을 추천한다.",
        backstory="정책 간 장단점, 대상 적합성, 혜택 효율성 등을 비교하여 사용자의 상황에 맞는 최적의 선택을 도출한다.",
        verbose=True,
        allow_delegation=False,
        llm=ChatOpenAI(model="gpt-4o-mini", temperature=0.4, max_tokens=1024),
        system_prompt=COMPARE_AGENT_PROMPT,
    )
