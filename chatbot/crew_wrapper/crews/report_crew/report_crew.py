import os

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from django.conf import settings

from chatbot.crew_wrapper.tools.plan_web_search_tool import plan_web_search_tool
from chatbot.crew_wrapper.tools.vector_meta_search_tool import vector_meta_search_tool
from chatbot.crew_wrapper.tools.vector_search_tool import vector_search_tool
from chatbot.crew_wrapper.tools.web_search_tool import web_search_tool


@CrewBase
class ReportCrew:
    """
    ReportCrew는 사용자의 질문과 프로필을 바탕으로
    최적의 공공서비스를 추천하고, 신청 전략을 수립한 뒤,
    최종적으로 마크다운 형식의 보고서로 정리하는 Crew입니다.

    이 Crew는 다음과 같은 과정을 순차적으로 수행합니다:

    1. 후보 서비스 검색 (recommend_services_task, web_search_task)
       - 사용자의 질문 키워드와 벡터 검색, 웹 검색을 통해 관련 서비스 정보를 수집합니다.
       - name/region 필터는 2글자 이하 핵심어만 사용합니다.

    2. 중복 통합 및 최종 추천 (select_final_services_task)
       - 수집된 결과에서 중복된 서비스를 통합하고, 사용자에게 가장 적합한 1~2개 서비스를 최종 선택합니다.

    3. 신청 전략 수립 (plan_application_strategy_task)
       - 선택된 서비스 수(1개/2개)에 따라 각각 다른 전략을 수립합니다.
       - 정보가 부족할 경우 `plan_web_search_tool`을 활용해 보완 검색을 수행합니다.
       - 전략은 마크다운 표 형식으로 작성됩니다.

    4. 최종 보고서 생성 (generate_recommendation_report_task)
       - 질문 요약, 추천 서비스 정보, 신청 전략, 기대 효과 등을 포함한 사용자 맞춤형 보고서를 생성합니다.

    사용되는 Agents:
        - recommend_service_selector
        - web_search_agent
        - final_service_selector
        - strategy_planner
        - report_writer

    사용되는 Tasks:
        - recommend_services_task
        - web_search_task
        - select_final_services_task
        - plan_application_strategy_task
        - generate_recommendation_report_task
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
    def recommend_service_selector(self) -> Agent:
        return Agent(
            config=self.agents_config["recommend_service_selector"],
            tools=[vector_search_tool, vector_meta_search_tool],
        )

    @agent
    def web_search_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["web_search_agent"],
            tools=[web_search_tool],
        )

    @agent
    def final_service_selector(self) -> Agent:
        return Agent(
            config=self.agents_config["final_service_selector"],
        )

    @agent
    def strategy_planner(self) -> Agent:
        return Agent(
            config=self.agents_config["strategy_planner"],
            tools=[plan_web_search_tool],
        )

    @agent
    def report_writer(self) -> Agent:
        return Agent(
            config=self.agents_config["report_writer"],
        )

    @task
    def recommend_services_task(self) -> Task:
        return Task(
            config=self.tasks_config["recommend_services_task"], async_execution=True
        )

    @task
    def web_search_task(self) -> Task:
        return Task(config=self.tasks_config["web_search_task"], async_execution=True)

    @task
    def select_final_services_task(self) -> Task:
        return Task(config=self.tasks_config["select_final_services_task"])

    @task
    def plan_application_strategy_task(self) -> Task:
        return Task(config=self.tasks_config["plan_application_strategy_task"])

    @task
    def generate_recommendation_report_task(self) -> Task:
        return Task(config=self.tasks_config["generate_recommendation_report_task"])

    # 크루 실행 정의
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[
                self.recommend_service_selector(),
                self.web_search_agent(),
                self.final_service_selector(),
                self.strategy_planner(),
                self.report_writer(),
            ],
            tasks=[
                self.recommend_services_task(),
                self.web_search_task(),
                self.select_final_services_task(),
                self.plan_application_strategy_task(),
                self.generate_recommendation_report_task(),
            ],
            process=Process.sequential,
            verbose=True,
            max_rpm=240,
        )
