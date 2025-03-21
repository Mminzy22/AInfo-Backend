from chatbot.crew_wrapper.recommend_crew.crew import create_recommend_crew


def run_recommend_crew(user_input: dict) -> str:
    """
    RecommendCrew를 실행하고 추천 결과를 반환합니다.

    Args:
        user_input (dict): {
            "user_id": int,
            "question": str,
            "filters": dict  # 예: {"나이": "29", "관심분야": "취업", "지역": "서울"}
        }

    Returns:
        str: 추천 결과 텍스트
    """
    crew = create_recommend_crew(user_input)

    return crew.kickoff()
