import time
from django.test import TestCase

from chatbot.crew_wrapper.crews.report_crew.report_crew import ReportCrew

class ReportCrewTestCase(TestCase):
    """
    ReportCrew의 전체 플로우를 테스트하는 Django 단위 테스트.
    """

    async def test_report_crew_kickoff_async(self):
        """
        ReportCrew가 정상적으로 kickoff_async를 수행하는지 테스트합니다.
        """

        # GIVEN: 유효한 입력값 세팅
        user_input = {
            "original_input": "기후동행 카드에 대해서 보고서 작성해줘",
            "keywords": "기후동행",
            "user_profile": {
                "region": "서울",
                "age": "29",
                "interests": "취업"
            }
        }

        # WHEN: ReportCrew 인스턴스 생성 및 kickoff_async 실행
        report_crew = ReportCrew()
        crew_instance = report_crew.crew()

        start_time = time.time()
        flow_result = await crew_instance.kickoff_async(inputs=user_input)
        end_time = time.time()

        # THEN: 결과 검증
        self.assertIsNotNone(flow_result, "Crew 실행 결과가 None입니다.")
        self.assertTrue(hasattr(flow_result, "raw"), "Crew 결과에 raw 속성이 없습니다.")
        self.assertIsInstance(flow_result.raw, str, "Crew 결과의 raw가 문자열이 아닙니다.")
        self.assertGreater(end_time - start_time, 0, "실행 시간이 0초 이하입니다.")

        print(f"ReportCrew 테스트 완료: 실행 시간 {end_time - start_time:.2f}초")
        print(f"생성된 보고서 일부 미리보기: {flow_result.raw[:500]}...")
