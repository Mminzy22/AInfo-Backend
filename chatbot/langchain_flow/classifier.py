from enum import Enum


class Category(Enum):
    """
    사용자 입력 분류를 위한 카테고리 Enum 클래스.

    각 카테고리는 사용자 질문의 성격에 따라 분류됩니다:
    Attributes:
        OFF_TOPIC: 정책과 무관한 질문 또는 잡담 등 분류 대상이 아닌 입력.
        GOV_POLICY: 정책 전반 또는 추천을 요청하는 일반적인 질문.
        DETAIL_POLICY: 정책의 세부 조건, 신청 방법 등 구체적인 정보를 묻는 질문.
        REPORT_REQUEST: 정책에 대한 요약 보고서 또는 정리된 정보를 요청하는 질문.
        SUPPORT_RELATED: 정책이란 키워드가 아닌 지원, 도움 같은 키워드로 입력.
    """

    OFF_TOPIC = "off_topic"
    GOV_POLICY = "gov_policy"
    DETAIL_POLICY = "detail_policy"
    REPORT_REQUEST = "report_request"
    SUPPORT_RELATED = "support_related"


# 각 카테고리에 해당하는 키워드 라스트
KEYWORD_CATEGORY_MAP = {
    Category.GOV_POLICY.value: [
        "정책",
        "지원",
        "프로그램",
        "혜택",
        "주거지원",
        "청년지원",
        "복지",
        "정부지원",
        "대상자",
        "제도",
        "정부정책",
        "복지정책",
        "지원정책",
        "지원제도",
        "청년정책",
        "창업지원",
        "금융지원",
        "취업지원",
        "일자리",
        "공공지원",
        "청년주택",
        "임대주택",
        "국가정책",
        "지원방안",
        "제도안내",
    ],
    Category.DETAIL_POLICY.value: [
        "대상",
        "선정기준",
        "신청방법",
        "신청사이트",
        "신청기한",
        "조건",
        "자격",
        "신청",
        "기간",
        "필요서류",
        "서류",
        "싱세",
        "자세히",
        "디테일",
        "절차",
        "증명서",
        "신청양식",
        "자세한내용",
        "서류제출",
        "제출서류",
        "신청조건",
        "신청절차",
        "신청링크",
        "접수기간",
        "자격요건",
        "자격조건",
        "신청가능일",
        "진행절차",
        "양식",
        "신청비용",
        "인터넷신청",
        "방문신청",
        "신청주소",
        "증빙자료",
        "첨부파일",
        "먼저",
    ],
}

# 'gov_policy' 으로 분류할 수 있는 질문/요청 패턴 목록
POLICY_PATTERNS = [
    "있어?",
    "있나요?",
    "알려줘",
    "뭐가 있어",
    "어떤 것이 있",
    "있는지",
    "받을 수 있",
    "지원받을 수",
    "혜택 받",
    "무슨 정책",
    "정책 알려줘",
    "지원해주는 게",
    "무슨 혜택",
    "혜택 종류",
    "받을 수 있는 정책",
    "관련된 정책",
    "지원 가능한 게",
    "추천해줘",
]
# 'detail_policy' 으로 분류할 수 있는 질문/요청 패턴 목록
DETAIL_PATTERNS = [
    "어떻게 신청",
    "어디서 신청",
    "신청 마감",
    "제출해야 하는",
    "필수 서류",
    "구체적",
    "상세 내용",
    "자세히",
    "어디서 확인",
    "언제까지 신청",
    "어떤 서류",
    "자격 요건",
    "자세한 정보",
    "신청하는 법",
    "신청 절차",
    "신청 주소",
    "신청 링크",
    "필요한 서류",
    "자세하",
    "상세",
]

# 키워드 매칭 시 가중치 점수 1, 패턴 매칭 시 가중치 점수 1.5
KEYWORD_SCORE = 1
PATTERN_SCORE = 2


def manual_classifier(user_message: str) -> str | None:
    """
    사용자 입력값을 키워드 및 문장 패턴을 기준으로 분류하는 함수입니다.

    키워드 및 문장 패턴을 사전에 정의해두고, 키워드랑 패턴 포함 정도에 따라
    'gov_policy'또는 'detail_policy' 카테고리로 분류합니다.
    사용자 입력값에 키워드가 포함되엉 있을 때마다 점수를 얻고(KEYWORD_SCORE), 패턴은 더 높은 점수(PATTERN_SCORE)를 얻습니다.
    최종적으로 더 높은 점수를 받은 카테고리를 반환하고, 0점이거나 동점일 때는 None을 반환합니다.

    Args:
        user_message (str): 사용자 입력 메시지

    Returns:
        str | None: 분류된 카테고리 문자열 ('gov_policy' 또는 'detail_policy') 또는 None.
    """

    scores = {Category.GOV_POLICY.value: 0, Category.DETAIL_POLICY.value: 0}

    for category, keywords in KEYWORD_CATEGORY_MAP.items():
        for keyword in keywords:
            if keyword in user_message:
                scores[category] += KEYWORD_SCORE

    for pattern in POLICY_PATTERNS:
        if pattern in user_message:
            scores[Category.GOV_POLICY.value] += PATTERN_SCORE

    for pattern in DETAIL_PATTERNS:
        if pattern in user_message:
            scores[Category.DETAIL_POLICY.value] += PATTERN_SCORE

    max_score = max(scores.values())

    if max_score == 0 or len(set(scores.values())) == 1:
        return None

    for category, score in scores.items():
        if score == max_score:
            return category
