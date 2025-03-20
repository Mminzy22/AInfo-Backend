from langchain.schema.runnable import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

from .memory import ChatHistoryManager
from .prompt import CHATBOT_PROMPT
from .retriever import VectorRetriever

# 리트리버 인스턴스 생성 (싱글톤으로 구현된 리트리버에 맞춰 전역 변수로 생성)
vector_retriever = VectorRetriever()
# 멀티쿼리리트리버로 변경함.
retriever = vector_retriever


async def get_chatbot_response(user_message, user_id):
    """
    비동기 스트리밍 방식 챗봇 응답을 생성할 수 있는 함수

    이 함수는 LangChain의 활용해서 검색 증강 생성(RAG) 방식의 챗봇 응답을 생성합니다.
    비동기 스트리밍으로 응답으로 실시간으로 반환하고, 대화 기록을 활용해 대화의 흐름을 이어나갈 수 있습니다.

    주요 기능:
    - 사용자의 입력을 받아 LLM을 실행하고, 비동기 스트리밍 방식으로 응답 바노한
    - 검색된 문서를 기반으로 하는 답변 제공
    - `ChatHistoryManager`를 통해 대화 내용을 관리할 수 있음
    - temperature=0.3: 창의성보다 정확도에 중점을 둠. (추후 조정 가능)


    변동사항 (03/09/25):
    - async, yield를 사용해 비동기 작업을 할 수 있도록 변경
    - LLM 응답을 invoke() 방식이 아닌 astream() 비동기 스트리밍 방식으로 변경

    변동사항 (03/19/25)
    - `ChatHistoryManager`를 통해 대화 내용 관리 및 멀티턴 기능 추가
    """

    # 사용자 질문을 기반으로 문서 검색
    retrieved_docs = retriever.search(user_message)

    # 디버깅: 검색된 문서가 있는지 확인
    if not retrieved_docs:
        print("검색된 문서가 없습니다.")
    else:
        pass

    # 검색된 문서를 문자열로 변환
    retrieved_context = retriever.format_docs(retrieved_docs)

    # RAG 검색 결과가 없으면 기본 context 사용
    if retrieved_context is None:
        retrieved_context = "정부의 지원 정책"

    # llm 실행 (CHATBOT_PROMPT는 utils1.py에서 import)
    # streaming 을 위한 streaming 파라미터 조정
    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.3, streaming=True)

    chat_manager = ChatHistoryManager(user_id, llm)
    memory_manager = chat_manager.get_memory_manager()
    memory = memory_manager.load_memory_variables({})

    prompt = CHATBOT_PROMPT

    rag_chain = (
        {
            "context": lambda _: retrieved_context,
            "question": RunnablePassthrough(),
            "chat_history": lambda _: memory.get("chat_history", []),
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    output_response = ""

    async for chunk in rag_chain.astream(user_message):
        output_response += chunk
        yield chunk

    memory_manager.save_context({"human": user_message}, {"ai": output_response})
