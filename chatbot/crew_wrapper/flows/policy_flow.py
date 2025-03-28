import time

from crewai.flow.flow import Flow, listen, start
from litellm.exceptions import RateLimitError

from chatbot.crew_wrapper.crews.compare_crew.compare_crew import CompareCrew
from chatbot.crew_wrapper.crews.rag_crew.rag_crew import RAGCrew
from chatbot.crew_wrapper.crews.report_crew.report_crew import ReportCrew
from chatbot.crew_wrapper.crews.strategy_crew.strategy_crew import StrategyCrew
from chatbot.crew_wrapper.crews.web_crew.web_crew import WebCrew


class PolicyFlow(Flow):
    def __init__(self, user_input: dict):
        super().__init__()
        self.user_input = user_input

    @start()
    def rag_search(self):
        print("RAG 기반 검색 수행")
        crew_result = RAGCrew().crew(user_input=self.user_input).kickoff()
        self.state["crew_result"] = crew_result.raw
        return crew_result

    @listen(rag_search)
    def web_search(self):
        print("웹 검색 수행")
        web_result = WebCrew().crew(user_input=self.user_input).kickoff()
        self.state["web_result"] = web_result.raw
        return web_result

    @listen(web_search)
    def compare_services(self):
        print("정책 비교 Task 실행")
        retry_count = 0
        while retry_count < 3:
            try:
                compare_result = (
                    CompareCrew()
                    .crew(
                        user_input=self.user_input,
                        recommend_task=self.state["crew_result"],
                        web_search_task=self.state["web_result"],
                    )
                    .kickoff()
                )
                self.state["compare_result"] = compare_result.raw
                return compare_result
            except RateLimitError:
                wait = 3 + retry_count * 2
                print(
                    f"[RateLimit] compare_services {wait}초 대기 후 재시도... ({retry_count+1}/3)"
                )
                time.sleep(wait)
                retry_count += 1
        raise Exception("RateLimit: compare_services 크루 실행 실패")

    @listen(compare_services)
    def make_strategy(self):
        print("실행 전략 생성 중")
        retry_count = 0
        while retry_count < 3:
            try:
                strategy_result = (
                    StrategyCrew()
                    .crew(
                        user_input=self.user_input,
                        recommend_task=self.state["crew_result"],
                        web_search_task=self.state["web_result"],
                        compare_task=self.state["compare_result"],
                    )
                    .kickoff()
                )
                self.state["strategy_result"] = strategy_result.raw
                return strategy_result
            except RateLimitError:
                wait_time = 3 + retry_count * 2
                print(
                    f"🚧 [RateLimit] {wait_time}초 후 재시도합니다... ({retry_count+1}/3)"
                )
                time.sleep(wait_time)
                retry_count += 1

        raise Exception("RateLimit: 전략 생성 크루 실행 3회 실패")

    @listen(make_strategy)
    def generate_report(self):
        print("보고서 생성 중")
        retry_count = 0
        while retry_count < 3:
            try:
                report_result = (
                    ReportCrew()
                    .crew(
                        user_input=self.user_input,
                        recommend_task=self.state["crew_result"],
                        web_search_task=self.state["web_result"],
                        compare_task=self.state["compare_result"],
                        strategy_task=self.state["strategy_result"],
                    )
                    .kickoff()
                )
                self.state["report_result"] = report_result.raw
                return report_result
            except RateLimitError:
                wait = 3 + retry_count * 2
                print(
                    f"[RateLimit] generate_report {wait}초 대기 후 재시도... ({retry_count+1}/3)"
                )
                time.sleep(wait)
                retry_count += 1
        raise Exception("RateLimit: generate_report 크루 실행 실패")

    def run(self):
        return self.kickoff()
