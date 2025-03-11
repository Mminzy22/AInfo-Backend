from datetime import datetime

from langchain.prompts import (
    ChatPromptTemplate,
    FewShotPromptTemplate,
    HumanMessagePromptTemplate,
    PromptTemplate,
    SystemMessagePromptTemplate,
)

current_date = datetime.now()
current_year_month = f"{current_date.year}년 {current_date.month}월"

# 시스템 메세지

system_message = SystemMessagePromptTemplate.from_template(
    """
    당신은 대한민국 정부 정책 전문 상담 AI 어시스턴트입니다.
    정책 정보, 지원 제도, 규제 등에 대해 친절하고 정확하게 답변하세요.

    ## 응답 지침
    - 인사나 간단한 일상 대화에는 자연스럽게 응답하세요.
    - 정책 정보를 **구조화된 형식**으로 제공하세요.
    - 확실하지 않은 정보는 추측하지마세요.
    - 제공할 수 없는 질문에는 "정부 정책 관련 질문을 도와드릴 수 있습니다."라고 응답하세요.

    ## 정책 정보 제공 형식
    **정책명**: [정책 이름]
    **대상**: [지원 대상]
    **지원 내용**: [혜택 및 지원금]
    **신청 방법**: [절차]
    **기간**: [신청 가능 기간]
    ---

    ## 제한 사항
    - 신청 기간이 {{current_year_month}} 이전이면 "해당 정책의 신청 기간이 종료되었습니다."라고 안내하세요.
    """
)
# 사용자 메세지
user_prompt = HumanMessagePromptTemplate.from_template(
    """
    ## 참고 문서:
    {context}

    ## 사용자 질문:
    질문: {question}

    🔹 제공된 문서의 내용을 바탕으로 정확한 정보를 전달하세요.
    🔹 검색된 문서가 없거나 부족하면, 유사한 정보를 제공하거나 추가적인 확인 방법을 안내하세요.
    🔹 오늘은 {{current_year_month}}입니다. 신청 가능 기간이 {{current_year_month}} 이전인 정보는 제공하지 마세요.

    확장된 질의:
    """
)

# 예제 데이터 정의
examples = [
    {
        "question": "돈이 필요해",
        "expanded_query": "지원금 정책, 긴급 복지 지원, 소득 보조 제도",
    },
    {
        "question": "집 사고 싶어",
        "expanded_query": "주택 구입 지원, 청년 전세 대출, 내 집 마련 정책",
    },
    {
        "question": "정부에서 취업 도와주는 거 있어?",
        "expanded_query": "취업 지원금, 청년 일자리 프로그램, 고용 보조금",
    },
    {
        "question": "세금 혜택 뭐 있어?",
        "expanded_query": "근로장려금, 세금 감면, 부가가치세 환급",
    },
    {
        "question": "주거 정책 알려줘",
        "expanded_query": "주택 구입 지원, 청년 전세 대출, 내 집 마련 정책",
    },
]

# 예제 템플릿
example_prompt = PromptTemplate.from_template(
    "질문: {question}\n확장된 질의: {expanded_query}"
)

# few shot prompt 객체화
few_shot_prompt = FewShotPromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
    suffix="질문: {question}\n확장된 질의:",
    input_variables=["question"],
)


# ChatPromptTemplate과 통합하기
# 직접 FewShotPromptTemplate을 넣을 수 없으므로, format()을 사용하여 변환해야 함
few_shot_prompt_text = few_shot_prompt.format(question="{question}")


CHATBOT_PROMPT = ChatPromptTemplate.from_messages(
    [
        system_message,
        HumanMessagePromptTemplate.from_template(few_shot_prompt_text),
        user_prompt,
    ]
)
