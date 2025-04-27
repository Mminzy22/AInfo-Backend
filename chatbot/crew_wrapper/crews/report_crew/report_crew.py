import os

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from django.conf import settings

from chatbot.crew_wrapper.tools.vector_meta_search_tool import vector_meta_search_tool
from chatbot.crew_wrapper.tools.vector_search_tool import vector_search_tool
from chatbot.crew_wrapper.tools.web_search_tool import web_search_tool


@CrewBase
class ReportCrew:
    """
    ReportCrew는 사용자의 질문과 프로필을 바탕으로
    적합한 공공서비스를 검색, 추천, 비교하고
    최종적으로 보고서 형태로 정리하는 Crew 입니다.

    Agents:
        - 후보 서비스 검색 (candidate_searcher)
        - 최적 서비스 선택 (best_service_selector)
        - 상세 정보 검색 (service_detail_fetcher)
        - 관련 서비스 추천 및 비교 (related_service_recommender)
        - 최종 보고서 작성 (report_generator)

    Tasks:
        - 검색, 선택, 상세조회, 추천/비교, 보고서 작성 단계로 순차 실행됩니다.
    """

    agents_config = os.path.join(
        settings.BASE_DIR,
        "chatbot",
        "crew_wrapper",
        "crews",
        "report_crew",
        "config",
        "agents.yaml",
    )
    tasks_config = os.path.join(
        settings.BASE_DIR,
        "chatbot",
        "crew_wrapper",
        "crews",
        "report_crew",
        "config",
        "tasks.yaml",
    )

    @agent
    def candidate_searcher(self) -> Agent:
        return Agent(
            config=self.agents_config["candidate_searcher"],
            tools=[vector_search_tool, web_search_tool],
        )

    @agent
    def best_service_selector(self) -> Agent:
        return Agent(
            config=self.agents_config["best_service_selector"],
        )

    @agent
    def service_detail_fetcher(self) -> Agent:
        return Agent(
            config=self.agents_config["service_detail_fetcher"],
            tools=[vector_meta_search_tool, web_search_tool],
        )

    @agent
    def related_service_recommender(self) -> Agent:
        return Agent(config=self.agents_config["related_service_recommender"])

    @agent
    def report_generator(self) -> Agent:
        return Agent(
            config=self.agents_config["report_generator"],
        )

    @task
    def search_candidates_task(self) -> Task:
        return Task(config=self.tasks_config["search_candidates_task"])

    @task
    def select_best_services_task(self) -> Task:
        return Task(config=self.tasks_config["select_best_services_task"])

    @task
    def fetch_service_details_task(self) -> Task:
        return Task(config=self.tasks_config["fetch_service_details_task"])

    @task
    def recommend_or_compare_task(self) -> Task:
        return Task(config=self.tasks_config["recommend_or_compare_task"])

    @task
    def generate_report_task(self) -> Task:
        return Task(config=self.tasks_config["generate_report_task"])

    # 크루 실행 정의
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[
                self.candidate_searcher(),
                self.best_service_selector(),
                self.service_detail_fetcher(),
                self.related_service_recommender(),
                self.report_generator(),
            ],
            tasks=[
                self.search_candidates_task(),
                self.select_best_services_task(),
                self.fetch_service_details_task(),
                self.recommend_or_compare_task(),
                self.generate_report_task(),
            ],
            process=Process.sequential,
            verbose=True,
            max_rpm=240,
        )
