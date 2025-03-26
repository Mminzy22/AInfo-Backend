from crewai import Crew

from chatbot.crew_wrapper.crews.rag_crew.config.rag_search_task import (
    create_rag_search_task,
)
from chatbot.crew_wrapper.crews.rag_crew.config.reg_agent import get_rag_search_agent


class RAGCrew:
    def crew(self, user_input: dict) -> Crew:
        agent = get_rag_search_agent()
        task = create_rag_search_task(agent=agent, user_input=user_input)

        return Crew(agents=[agent], tasks=[task], verbose=True)
