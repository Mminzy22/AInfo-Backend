from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class PolicyQueryInput(BaseModel):
    question: str = Field(..., description="사용자 질문(원본 질문)")
    keywords: str = Field(..., description="검색 키워드")
    filters: Optional[Dict[str, str]] = Field(
        default=None,
        description="메타데이터 필터링 조건 (나이, 지역, 관심분야 등). 없으면 필터 없이 전체 검색",
    )
    collection_names: Optional[List[str]] = Field(
        default=None, description="검색할 컬렉션 이름 목록"
    )
    k: Optional[int] = Field(default=5, description="컬렉션당 검색 결과 개수")
