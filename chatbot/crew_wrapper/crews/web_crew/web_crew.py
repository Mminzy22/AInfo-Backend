from crewai import Crew

from chatbot.crew_wrapper.crews.web_crew.config.web_search_agent import (
    get_web_search_agent,
)
from chatbot.crew_wrapper.crews.web_crew.config.web_search_task import (
    create_web_search_task,
)


class WebCrew:
    def crew(self, user_input: dict) -> Crew:
        agent = get_web_search_agent()
        task = create_web_search_task(agent=agent, user_input=user_input)

        return Crew(agents=[agent], tasks=[task], verbose=True)
