from crewai import Crew

from chatbot.crew_wrapper.crews.compare_crew.config.compare_agent import (
    get_compare_agent,
)
from chatbot.crew_wrapper.crews.compare_crew.config.compare_task import (
    create_compare_task,
)


class CompareCrew:
    def crew(self, user_input: dict, recommend_task: str, web_search_task: str) -> Crew:
        print(type(recommend_task))
        agent = get_compare_agent()
        task = create_compare_task(
            agent=agent,
            user_input=user_input,
            recommend_task=recommend_task,
            web_search_task=web_search_task,
        )

        return Crew(agents=[agent], tasks=[task], verbose=True)
