from langchain.schema.runnable import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

from .prompt import CHATBOT_PROMPT
from .retriever import VectorRetriever

# 리트리버 인스턴스 생성 (싱글톤으로 구현된 리트리버에 맞춰 전역 변수로 생성)
vector_retriever = VectorRetriever()
retriever = vector_retriever.get_retriever()


def get_chatbot_response(user_message):
    """
    - 사용자의 입력을 받아 LLM을 실행하고, 단일 응답만 반환 (싱글턴, 대화 기록 저장 X)
    - temperature=0.3: 창의성보다 정확도에 중점을 둠. (추후 조정 가능)
    """

    # 사용자 질문을 기반으로 문서 검색
    retrieved_docs = retriever.invoke(user_message)

    # 디버깅: 검색된 문서가 있는지 확인
    if not retrieved_docs:
        print("검색된 문서가 없습니다.")
    else:
        pass

    # 검색된 문서를 문자열로 변환
    retrieved_context = VectorRetriever().format_docs(retrieved_docs)

    # RAG 검색 결과가 없으면 기본 context 사용
    if retrieved_context is None:
        retrieved_context = "정부의 지원 정책"

    # llm 실행 (CHATBOT_PROMPT는 utils1.py에서 import)
    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.3)

    prompt = CHATBOT_PROMPT

    rag_chain = (
        {"context": lambda _: retrieved_context, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    response = rag_chain.invoke(user_message)

    return {
        "response": response,
        "retrieved_context": retrieved_context,  # RAG에서 가져온 문서 같이 출력되도록 함(확인용)
    }
