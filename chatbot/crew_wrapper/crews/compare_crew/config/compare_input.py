from typing import Dict, Optional

from pydantic import BaseModel, Field


class ComparePolicyInput(BaseModel):
    question: str = Field(
        ..., description="사용자의 원래 질문. 어떤 정책을 찾고 있는지를 나타냅니다."
    )
    previous_result: str = Field(
        ...,
        description="이전에 추천된 공공서비스 결과 텍스트. 비교 분석 대상이 되는 정책 정보입니다.",
    )
    filters: Optional[Dict[str, str]] = Field(
        default=None,
        description="사용자 프로필 기반의 필터 조건 (예: 나이, 지역, 관심분야 등). 비교에 참고할 수 있습니다.",
    )
