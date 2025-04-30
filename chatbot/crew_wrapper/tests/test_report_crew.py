from unittest.mock import AsyncMock, patch

from django.test import TestCase

from chatbot.crew_wrapper.crews.report_crew.report_crew import ReportCrew


class ReportCrewTestCase(TestCase):
    """
    ReportCrew의 전체 플로우를 테스트하는 Django 단위 테스트 (Mock 적용 버전).
    """

    @patch(
        "chatbot.crew_wrapper.crews.report_crew.report_crew.Crew.kickoff_async",
        new_callable=AsyncMock,
    )
    async def test_report_crew_kickoff_async(self, mock_kickoff_async):
        """
        ReportCrew가 정상적으로 kickoff_async를 호출하는지만 테스트합니다.
        (LLM API 호출 없이 빠르게 테스트합니다)
        """

        user_input = {
            "original_input": "나는 경기도에 살아. 나한테 경기패스가 좋을지 기후동행 카드가 좋을지에 대해서 보고서 작성해줘",
            "summary": "경기도 청년에게 적합한 교통비 지원 공공서비스 비교: 경기패스 vs 기후동행카드",
            "keywords": "경기패스 기후동행카드 경기도",
            "user_profile": {"region": "경기도 안산시", "age": "30", "interests": "취업"},
        }

        mock_kickoff_async.return_value = AsyncMock(raw="Mocked Report Content")

        report_crew = ReportCrew()
        crew_instance = report_crew.crew()
        flow_result = await crew_instance.kickoff_async(inputs=user_input)

        # 결과 검증
        self.assertIsNotNone(flow_result, "Crew 실행 결과가 None입니다.")
        self.assertTrue(hasattr(flow_result, "raw"), "Crew 결과에 raw 속성이 없습니다.")
        self.assertIsInstance(
            flow_result.raw, str, "Crew 결과의 raw가 문자열이 아닙니다."
        )
