from crewai import Crew

from chatbot.crew_wrapper.crews.strategy_crew.config.strategy_agent import (
    get_strategy_agent,
)
from chatbot.crew_wrapper.crews.strategy_crew.config.strategy_task import (
    create_strategy_task,
)


class StrategyCrew:
    def crew(
        self,
        user_input: dict,
        recommend_task: str,
        web_search_task: str,
        compare_task: str,
    ) -> Crew:
        agent = get_strategy_agent()
        task = create_strategy_task(
            agent=agent,
            user_input=user_input,
            recommend_task=recommend_task,
            web_search_task=web_search_task,
            compare_task=compare_task,
        )

        return Crew(agents=[agent], tasks=[task], verbose=True)
