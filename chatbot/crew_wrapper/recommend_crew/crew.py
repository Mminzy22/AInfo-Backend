from crewai import Crew

from chatbot.crew_wrapper.recommend_crew.agents import rag_search_agent, recommendation_agent
from chatbot.crew_wrapper.recommend_crew.tasks.generate_recommendation_task import create_recommendation_task
from chatbot.crew_wrapper.recommend_crew.tasks.rag_search_task import create_rag_search_task


def create_recommend_crew(user_input: dict) -> Crew:
    """
    사용자 질문과 필터 조건을 기반으로 RAG 검색 및 추천 Task를 구성한 Crew 객체를 생성합니다.

    Args:
        user_input (dict): {
            "user_id": int,
            "question": str,
            "filters": dict
        }

    Returns:
        Crew: CrewAI 실행을 위한 RecommendCrew 인스턴스
    """
    # Task 1: RAG 검색
    rag_task = create_rag_search_task(agent=rag_search_agent, user_input=user_input)

    # Task 2: 추천 요약
    recommendation_task = create_recommendation_task(agent=recommendation_agent, user_input=user_input, rag_task=rag_task)

    return Crew(
        agents=[rag_search_agent, recommendation_agent],
        tasks=[rag_task, recommendation_task],
        verbose=True
    )