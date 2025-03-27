from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.tools.render import render_text_description
from langchain_openai import ChatOpenAI

from ..memory import ChatHistoryManager
from ..prompts.search_prompt import get_news_search_prompt
from ..tools.tavily_news_tool import news_search_tool

"""
LangChain 뉴스 검색 에이전트를 구성하는 실행 모듈입니다.

- 도구: Tavily 기반 뉴스 검색 툴
- 프롬프트: 2025년 기준 뉴스 요약 포맷
- LLM: OpenAI gpt-4o-mini
- 메모리: 요약 기반 멀티턴 메모리
- 에이전트: OpenAI Function Agent
- 실행기: AgentExecutor
"""


def get_news_search_executor(user_id: str) -> AgentExecutor:
    tools = [news_search_tool]

    prompt = get_news_search_prompt(tools).partial(
        tools_description=render_text_description(tools)
    )

    llm = ChatOpenAI(model="gpt-4o", temperature=0)

    memory = ChatHistoryManager(user_id=user_id, model=llm).get_memory_manager()

    agent = create_openai_functions_agent(llm=llm, tools=tools, prompt=prompt)

    return AgentExecutor(agent=agent, tools=tools, memory=memory, verbose=True)
