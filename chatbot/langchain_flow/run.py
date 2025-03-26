from langchain_openai import ChatOpenAI
from chatbot.langchain_flow.memory import ChatHistoryManager
from chatbot.langchain_flow.prompt import CLASSIFICATION_PROMPT
from langchain_core.output_parsers import JsonOutputParser
from chatbot.langchain_flow.classifier import manual_classifier, Category
from chatbot.langchain_flow.profile import get_profile_data
from chatbot.langchain_flow.chains.overview_rag_chain import OVERVIEW_CHAIN
from chatbot.langchain_flow.chains.detail_rag_chain import DETAIL_CHAIN


async def get_chatbot_response(user_message: str, user_id: str, room_id: str):
    """
    사용자 메시지를 기반으로 검색 증강 생성(RAG) 방식의 응답을 스트리밍 방식으로 생성하는 함수.

    이 함수는 LangChain의 활용해서 사용자 입력을 분류하고 해당 분류에 따라 적절한 RAG 체인을 선택하여 응답을 생성합니다.
    비동기 스트리밍으로 응답으로 실시간으로 반환하고, 대화 기록을 활용해 대화의 흐름을 이어나갈 수 있습니다.

    주요 기능:
    - 사용자의 입력을 받아 LLM을 사용자 입력을 분류하고, 체인을 활용한 검색 증강 생성(RAG) 답변을 비동기 스트리밍 방식으로 반환
    - LLM 기반 입력 분류 + 수동 규칙 기반 보정(manual classifier)
    - 분류 결과에 따라 체인 분기 처리 (개요 / 상세 정책 / 보고서 요청 등)
    - 검색된 문서를 기반으로 하는 답변 제공
    - Django Redis 기반 `ChatHistoryManager`를 통해 대화 내용을 관리할 수 있음

    변동사항 (03-26-25)
    - 입력 분류(classification) 기능 추가, 프로필 키워드 기반 맥락 보강, 분류 결과에 따른 체인 분기 로직 구현

    변동사항 (03/19/25)
    - `ChatHistoryManager`를 통해 대화 내용 관리 및 멀티턴 기능 추가

    변동사항 (03/09/25):
    - async, yield를 사용해 비동기 작업을 할 수 있도록 변경
    - LLM 응답을 invoke() 방식이 아닌 astream() 비동기 스트리밍 방식으로 변경

    Args:
        user_message (str): 사용자의 질문 또는 입력 메시지
        user_id (str): 사용자 ID
        room_id (str): 대화방 ID

    Yields:
        str: 실시간으로 생성된 응답의 텍스트 청크
    """

    # 멀티턴을 위한 레디스 메모리 매니저 인스턴스 생성 & 대화내용 요약을 위한 LLM 로드
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3, streaming=True)
    chat_manager = ChatHistoryManager(user_id, room_id, llm)
    memory = chat_manager.get_memory_manager()
    chat_history = memory.load_memory_variables({}).get("chat_history", [])

    # 1차적으로 LLM이 사용자 입력을 분류하고 중요 키워드 추출
    classification_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
    classification_chain = (
        CLASSIFICATION_PROMPT | classification_llm | JsonOutputParser()
    )
    classification_result = await classification_chain.ainvoke(
        {"question": user_message, "chat_history": chat_history}
    )

    # 2차적으로 LLM이 한국말의 문맥을 판단 못하는 경우를 대비해서 특정 키워드가 있으면 분류 결과 재조정
    manual_category = manual_classifier(user_message)

    if (
        classification_result["is_followup"]
        and manual_category == Category.DETAIL_POLICY.value
    ):
        classification_result["category"] = Category.DETAIL_POLICY.value
    elif manual_category and manual_category != classification_result["category"]:
        classification_result["category"] = manual_category

    category = classification_result["category"]

    # 유저 프로필 정보 및 키워드 추출
    profile_data = await get_profile_data(int(user_id))

    profile_keywords = profile_data["keywords"]
    profile = profile_data["profile"]

    llm_keywords = classification_result.get("keywords", [])

    # 사용자 입력에 따른 분기 처리
    if category == Category.OFF_TOPIC.value:
        yield "정책 및 지원에 관한 내용을 물어봐주시면 친절하게 답변해드릴 수 있습니다."
        return

    elif category in [Category.GOV_POLICY.value, Category.SUPPORT_RELATED.value]:
        chain = OVERVIEW_CHAIN

    elif category == Category.DETAIL_POLICY.value:
        chain = DETAIL_CHAIN

    elif category == Category.REPORT_REQUEST.value:
        yield "보고서 작성 서비스는 곧 만나보실 수 있습니다."
        return

    else:
        yield "죄송합니다. 질문을 절확히 이해하지 못했습니다. 다시 한번 질문해주실 수 있을까요?"

    # 스트리밍 실행
    output_response = ""
    async for chunk in chain.astream(
        {
            "question": classification_result["original_input"],
            "keywords": llm_keywords,
            "chat_history": chat_history,
            # "profile": profile,
        }
    ):
        output_response += chunk
        yield chunk

    # 멀티턴 메모리에 저장
    memory.save_context({"human": user_message}, {"ai": output_response})
