from crewai import Agent
from langchain_openai import ChatOpenAI

from chatbot.crew_wrapper.crews.report_crew.config.prompts import REPORT_AGENT_PROMPT


def get_report_agent():
    return Agent(
        role="공공정책 분석 보고서 작성 전문가",
        goal="사용자 질문과 분석 결과를 바탕으로 사용자가 이해하기 쉬운 공공서비스 전략 보고서를 작성한다.",
        backstory=(
            "다양한 정책 정보를 종합하여 사용자가 쉽게 이해할 수 있는 분석 보고서를 작성. "
            "정책의 핵심 정보를 파악하여 전문적인 스타일로 작성합니다."
        ),
        verbose=True,
        allow_delegation=False,
        llm=ChatOpenAI(model="gpt-4o-mini", temperature=0.7, max_tokens=3000),
        system_prompt=REPORT_AGENT_PROMPT,
    )
