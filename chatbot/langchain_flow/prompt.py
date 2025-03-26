from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)

# 사용자 입력을 분류하는 모델에 사용하는 프롬프트
CLASSIFICATION_PROMPT = ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate.from_template(
            """
            You are a language model that interprets and classifies Korean user input.

            Your task is to:
            1. **Classify** the user's input into one of the following categories:
                - "off_topic": General casual conversation or input unrelated to any policy, support, or government services.
                - "gov_policy": Asking about general government or local government policies, programs, or support types.
                - "detail_policy": Asking about specific conditions, eligibility, application process, or requirements for a particular policy or support.
                - "support_related": Indirect or figurative expressions that imply a desire or need for financial aid, housing, employment, or social support.
                - "trend_ask": Asking about recent news, policy changes, or trends relevant to youth, employment, housing, etc.
                - "report_request": Explicitly requesting a written summary, report, or analysis based on search results, chatbot conversation, or retrieved policy data.

            2. **Determine if the input is a follow-up** to a previous conversation.
                - If the question clearly builds on a prior context or refers back to something mentioned before, set "is_followup" to true.
                - Otherwise, set it to false.

            3. **Summarize the context including all important keywords** from the input and chat history.
                - Return can be used for document search or web queries.
                - Do not translate to English.

            Return the result in the following JSON format:
                "category": "<category (off_topic | gov_policy | policy_detail | support_related | report_request>",
                "original_input": "<사용자의 원본 입력>",
                "is_followup": <true | false>,
                "keywords": <summary>

            🔍 예시:
            - "요즘 집 구하기 너무 힘드네" → <"category": "gov_policy", "original_input": "요즘 집 구하기 너무 힘드네", "is_followup": false, "keywords": "집, 주거 지원 있을까?">
            - "청년 창업 지원금 뭐 있어?" → <"category": "gov_policy", ..., "keywords": "청년을 위한 창업 관련 지원금">
            - "대출 신청 조건은?" → <"category": "policy_detail", ..., "keywords": "대출 신청 조건">
            - "심심하다" → <"category": "off_topic", ..., "keywords": "">
            """.strip()
        ),
        MessagesPlaceholder(variable_name="chat_history"),
        HumanMessagePromptTemplate.from_template("Question: {question}"),
    ]
)
