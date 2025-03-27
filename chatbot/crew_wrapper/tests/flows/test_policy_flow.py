from unittest.mock import MagicMock, patch

from django.test import TestCase

from chatbot.crew_wrapper.flows.policy_flow import PolicyFlow


class PolicyFlowTest(TestCase):

    @patch("chatbot.crew_wrapper.crews.report_crew.report_crew.ReportCrew.crew")
    @patch("chatbot.crew_wrapper.crews.strategy_crew.strategy_crew.StrategyCrew.crew")
    @patch("chatbot.crew_wrapper.crews.compare_crew.compare_crew.CompareCrew.crew")
    @patch("chatbot.crew_wrapper.crews.web_crew.web_crew.WebCrew.crew")
    @patch("chatbot.crew_wrapper.crews.rag_crew.rag_crew.RAGCrew.crew")
    def test_policy_flow_execution(
        self,
        mock_rag_crew,
        mock_web_crew,
        mock_compare_crew,
        mock_strategy_crew,
        mock_report_crew,
    ):

        mock_rag_crew.return_value.kickoff.return_value = MagicMock(raw="Mock RAG 결과")
        mock_web_crew.return_value.kickoff.return_value = MagicMock(
            raw="Mock 웹 검색 결과"
        )
        mock_compare_crew.return_value.kickoff.return_value = MagicMock(
            raw="Mock 비교 결과"
        )
        mock_strategy_crew.return_value.kickoff.return_value = MagicMock(
            raw="Mock 전략 결과"
        )
        mock_report_crew.return_value.kickoff.return_value = MagicMock(
            raw="Mock 보고서 결과"
        )

        # 테스트용 입력값
        user_input = {
            "original_input": "서울 청년 창업 정책 알려줘",
            "summary": "이전에 창업 정책 질문함",
            "keywords": ["서울", "청년", "창업"],
            "user_profile": {"지역": "서울", "나이": "28", "관심분야": "창업"},
        }

        # Flow 실행
        flow = PolicyFlow(user_input)
        result = flow.run()

        # 결과 확인: .raw 값 비교
        self.assertEqual(result.raw, "Mock 보고서 결과")

        # 각 crew가 실행되었는지 확인
        mock_rag_crew.assert_called_once()
        mock_web_crew.assert_called_once()
        mock_compare_crew.assert_called_once()
        mock_strategy_crew.assert_called_once()
        mock_report_crew.assert_called_once()
