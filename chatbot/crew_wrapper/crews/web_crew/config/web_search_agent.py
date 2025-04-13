from crewai import Agent
from langchain_openai import ChatOpenAI

from chatbot.crew_wrapper.crews.web_crew.config.prompts import WEB_SEARCH_AGENT_PROMPT


def get_web_search_agent():
    return Agent(
        role="공공서비스 웹검색 추천 전문가",
        goal="사용자의 질문과 프로필을 기반으로 맞춤형 공공정책을 추천한다.",
        backstory="정책 정보를 분석하여 사용자에게 꼭 맞는 추천을 도와준다.",
        verbose=True,
        allow_delegation=False,
        llm=ChatOpenAI(model="gpt-4o-mini", temperature=0.1, max_tokens=1024),
        system_prompt=WEB_SEARCH_AGENT_PROMPT,
        max_rpm=3,
    )
