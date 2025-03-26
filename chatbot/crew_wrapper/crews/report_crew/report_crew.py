from crewai import Crew

from chatbot.crew_wrapper.crews.report_crew.config.report_agent import get_report_agent
from chatbot.crew_wrapper.crews.report_crew.config.report_task import create_report_task


class ReportCrew:
    def crew(
        self,
        user_input: dict,
        recommend_task: str,
        web_search_task: str,
        compare_task: str,
        strategy_task: str,
    ) -> Crew:
        agent = get_report_agent()
        task = create_report_task(
            agent=agent,
            user_input=user_input,
            recommend_task=recommend_task,
            web_search_task=web_search_task,
            compare_task=compare_task,
            strategy_task=strategy_task,
        )

        return Crew(agents=[agent], tasks=[task], verbose=True)
