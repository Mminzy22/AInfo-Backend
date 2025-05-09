import asyncio
import time
from typing import TypedDict, Annotated, AsyncGenerator
from datetime import datetime, date
from langgraph.graph.message import add_messages
from channels.db import database_sync_to_async
from django.db import transaction
from accounts.models import User
from langchain_openai import ChatOpenAI
from chatbot.langchain_flow.prompt import CLASSIFICATION_PROMPT
from langchain_core.output_parsers import JsonOutputParser
from chatbot.langchain_flow.classifier import Category, manual_classifier
from chatbot.langchain_flow.profile import get_profile_data
from chatbot.langchain_flow.chains.detail_rag_chain import DETAIL_CHAIN
from chatbot.langchain_flow.chains.overview_rag_chain import OVERVIEW_CHAIN
from chatbot.langchain_flow.chains.personalized_rag_chain import PERSONALIZED_CHAIN
from chatbot.langchain_flow.memory import ChatHistoryManager
from langchain.prompts import PromptTemplate
from langchain.schema.output_parser import StrOutputParser
from chatbot.langgraph_flow.prompts.analyze_prompt import ANALYZE_PROMPT
from chatbot.langgraph_flow.prompts.final_answer_prompt import FINAL_ANSWER_PROMPT
from chatbot.langgraph_flow.prompts.relevance_check_prompt import RELEVANCE_CHECK_PROMPT
from chatbot.langgraph_flow.utils_profile import get_interest, get_education, get_job_status, get_location, get_age
from chatbot.retriever import VectorRetriever
from langchain_tavily import TavilySearch

from langgraph.graph import StateGraph, END, START


# ------- State 정의 -------
class ChatbotState(TypedDict):
    user_message: str
    user_id: int
    room_id: str
    is_report: bool
    chat_history: Annotated[list, add_messages]
    
    is_relevant: str # 사용자 질문이 지원정책, 제도와 관련있는지 판별 -> "Y" or "N"
    interest: str
    education: str
    job_status: str
    location: str
    age: str
    
    retrieved_docs: str
    web_docs: str
    final_context: str
    search_retry_count: int
    web_search: str  # RAG 검색된 문서기반 웹검색이 필요한지 판별 -> "Y" or "N"
    web_search_query: str


# ------- 크레딧 차감 함수 -------
@database_sync_to_async
def check_and_deduct_credit(user_id: int, cost: int = 1) -> User:
    with transaction.atomic():
        user = User.objects.select_for_update().get(id=user_id)
        if user.credit < cost:
            raise ValueError(f"AInfo를 이용하기 위해서는 최소 {cost} 크레딧이 필요합니다.")
        user.credit -= cost
        user.save()
        return user


# ------- 노드 정의 -------
# 질문 분석 노드
async def analyze_user_message(state: ChatbotState) -> ChatbotState:
    """
    Description: 사용자 질문을 분석하는 노드
    
    - 정책관련성 및 개인정보(관심사, 학력, 직업상태, 거주지, 나이정보)를 분석
    - 정형화된 답변과 정확성을 올리기 위한 few-shot 프롬프팅, llm모델 temperature=0 적용
    """
    print(f"질문 분석 노드 시작")
    start_time = time.time()
    
    user_input = state["user_message"]
    current_year = datetime.now().year
    prompt = ANALYZE_PROMPT
    chain = prompt | ChatOpenAI(model="gpt-4o-mini", temperature=0) | JsonOutputParser()
    
    result = await chain.ainvoke({"question": user_input, "current_year": current_year})
    end_time = time.time()
    print(f"분석상태 : {result}")
    print(f"질문 분석 노드 완료 -> 소요시간 : {end_time - start_time:.2f}초")
    return {**state, **result}


# 질문 관련성 조건분기 위한 함수
async def message_relevance_check(state: ChatbotState) -> dict:
    """
    Description: 제도, 정책과 관련없는 질문은 그래프 종료하기위한 함수
    """
    flag = "Y"
    if state["is_relevant"] == "N":
        flag = "N"
    return {"next": flag}


# 프로필 정보 보완을 목적으로 조건분기 위한 함수
async def profile_check(state: ChatbotState) -> dict:
    """
    Description: DB쿼리 최소화를 위한 프로필정보 보완 노드를 무시하도록 분기처리하는 함수
    
    - 사용자 질문에 개인정보가 포함되어 있다면 "N" 반환 -> 리트리버 노드로 이동
    - 개인정보가 없다면 "Y" 반환 -> 프로필정보 보완 노드로 이동
    """
    print(f"프로필체크 노드 시작")
    start_time = time.time()
    
    flag = "Y"
    if state["education"] and state["job_status"] and state["location"] and state["age"]:
        flag = "N"
    
    end_time = time.time()
    print(f"프로필체크 노드 완료 -> 소요시간 : {end_time - start_time:.2f}초")
    
    return {"next": flag}



# 프로필정보 보완 노드
@database_sync_to_async
def get_user(user_id):
    return User.objects.get(pk=user_id)

async def fill_missing_profile(state: ChatbotState) -> ChatbotState:
    """
    Description: 질문에 사용자 개인정보가 없다면 프로필정보를 기반으로 정보를 보완하는 노드
    """
    print(f"프로필정보 보완 노드 시작")
    start_time = time.time()
    
    user = await get_user(state["user_id"])
    
    interest = state.get("interest", "") if state.get("interest", "") not in (None, "", []) else await get_interest(user)
    education = state.get("education", "") if state.get("education", "") not in (None, "", []) else await get_education(user)
    job_status = state.get("job_status", "") if state.get("job_status", "") not in (None, "", []) else await get_job_status(user)
    location = state.get("location", "") if state.get("location", "") not in (None, "", []) else await get_location(user)
    age = state.get("age", "") if state.get("age", "") not in (None, "", []) else await get_age(user)
    
    end_time = time.time()
    print(f"프로필정보 보완 노드 완료 -> 소요시간 : {end_time - start_time:.2f}초")
    
    return {
        **state,
        "interest": interest,
        "education": education,
        "job_status": job_status,
        "location": location,
        "age": age
    }

# 리트리버 노드
async def search_vector_db(state: ChatbotState) -> ChatbotState:
    """
    Description: 사용자 질문기반 정보 + 프로필 기반 정보 를 바탕으로 문서 검색을 하는 노드
    """
    
    print(f"리트리버 노드 시작")
    start_time = time.time()
    
    query = f"""
                나이 : {state["age"]}
                학력 : {state["education"]}
                거주지 : {state["location"]}
                직업상태 : {state["job_status"]}
                관심사 : {state["interest"]}
                인 사용자가 
                질문 : {state["user_message"]}
                에 대해 받을 수 있는 지원 정책이나 혜택 정보를 검색해
            """
    retriever = VectorRetriever()
    
    docs = retriever.search(query=query, k=3)
    docs_formatted = retriever.format_docs(docs)
    
    end_time = time.time()
    print(f"docs원문 -> {docs}")
    print("------"*18)
    print(f"docs포맷버전 -> {docs_formatted}")
    print(f"리트리버 노드 완료 -> 소요시간 : {end_time - start_time:.2f}초")
    
    return {**state, "retrieved_docs": docs_formatted}


# 검색 품질 검사 노드
async def docs_relevance_check(state: ChatbotState) -> ChatbotState:
    """
    Description: RAG 검색 문서의 품질을 검사하는 노드
    
    - 사용자 정보(학력, 직업상태, 거주지, 나이) 와 현재날짜를 기반으로 정책의 제한사항에 부합하는지 판별
    - 최종 문서의 갯수가 5개 이하라면 web_search 의 값을 "Y" 로 반환
    """
    print(f"검색 품질 검사 노드 시작")
    start_time = time.time()
    
    docs = state["retrieved_docs"]
    education = state["education"]
    job_status = state["job_status"]
    location = state["location"]
    age = state["age"]
    current_year = datetime.now().year
    prompt = RELEVANCE_CHECK_PROMPT
    chain = prompt | ChatOpenAI(model="gpt-4o-mini", temperature=0) | JsonOutputParser()
    result = await chain.ainvoke({
        "current_year": current_year,
        "docs": docs,
        "education": education,
        "job_status": job_status,
        "location": location,
        "age": age
    })
    
    end_time = time.time()
    print(f"검사 상태 : {result}")
    print(f"검색 품질 검사 노드 완료 -> 소요시간 : {end_time - start_time:.2f}초")
    
    return {**state, **result}


# 웹 검색노드로 조건분기 위한 함수
async def web_search_check(state:ChatbotState) -> dict:
    """
    Description: 웹검색이 필요하면 웹검색노드로 조건분기 하기위한 함수
    """
    
    flag = "Y"
    if state["web_search"] == "N":
        flag = "N"
    return {"next": flag}


# 웹검색을 진행하는 노드
async def search_web(state:ChatbotState) -> ChatbotState:
    """
    Description: 웹검색을 진행하는 노드
    
    - Tavily의 검색엔진은 semantic retrieval 기반 -> 키워드보단 사용자의 질문을 요약한 자연어 쿼리로 검색진행
    - 신뢰도 높은 도메인 (gov.kr, moel.go.kr 등) 에서 공공서비스 정보를 검색
    """
    
    print(f"웹검색 노드 시작")
    start_time = time.time()
    
    query = state["web_search_query"]
    
    tavily_search = TavilySearch(
        max_results=5,
        topic="general",
        include_answer=True,
        include_raw_content=True,
        search_depth="advanced",
        time_range="year",
        include_domains=[
            "gov.kr", "moel.go.kr", "work24.go.kr",
            "k-startup.go.kr", "youthcenter.go.kr",
            "mohw.go.kr", "bokjiro.go.kr", "seoul.go.kr", "gg.go.kr"
        ],
    )
    result = tavily_search.invoke({"query": query})
    
    end_time = time.time()
    print(f"웹검색 결과 : {result}")
    print(f"웹검색 노드 완료 -> 소요시간 : {end_time - start_time:.2f}초")
    
    return {**state, "web_docs": result}



# ------- 그래프 구축 -------
graph = StateGraph(ChatbotState)

# 노드 등록
graph.add_node("analyze_user_message", analyze_user_message)
graph.add_node("message_relevance_check", message_relevance_check)
graph.add_node("profile_check", profile_check)
graph.add_node("fill_missing_profile", fill_missing_profile)
graph.add_node("search_vector_db", search_vector_db)
graph.add_node("docs_relevance_check", docs_relevance_check)
graph.add_node("web_search_check", web_search_check)
graph.add_node("search_web", search_web)

# 흐름 연결
graph.add_edge(START, "analyze_user_message")
graph.add_edge("analyze_user_message", "message_relevance_check")
graph.add_conditional_edges(
    "message_relevance_check",
    lambda state: state["next"],
    {
        "Y": "profile_check",
        "N": END
    }
)
graph.add_conditional_edges(
    "profile_check",
    lambda state: state["next"],
    {
        "Y": "fill_missing_profile",
        "N": "search_vector_db"
    }
)
graph.add_edge("fill_missing_profile", "search_vector_db")
graph.add_edge("search_vector_db", "docs_relevance_check")
graph.add_edge("docs_relevance_check", "web_search_check")
graph.add_conditional_edges(
    "web_search_check",
    lambda state: state["next"],
    {
        "Y": "search_web",
        "N": END
    }
)
graph.add_edge("search_web", END)

chatbot_flow = graph.compile()


# ------- 메인 실행 함수 -------
async def get_chatbot_response_v2(user_message: str, user_id: int, room_id: str, is_report: bool):
    initial_state = {
        "user_message": user_message,
        "user_id": int(user_id),
        "room_id": room_id,
        "is_report": is_report,
        "chat_history": [],
        "retrieved_docs": "",
        "web_docs": "",
        "age": "",
        "web_search_query": ""
        
    }
    
    # 랭그래프 분기 처리
    final_state = await chatbot_flow.ainvoke(initial_state)
    # 필요데이터 파싱
    is_relevant = final_state["is_relevant"]
    interest = final_state["interest"]
    education = final_state["education"]
    job_status = final_state["job_status"]
    location = final_state["location"]
    age = final_state["age"]
    retrieved_docs = final_state["retrieved_docs"]
    web_docs = final_state["web_docs"]
    web_search_query = final_state["web_search_query"]
    
    # 관련없는 질문 처리
    if is_relevant == "N":
        yield "정책 및 지원에 관한 내용을 물어봐주시면 친절하게 답변해드릴 수 있습니다."
        return
    
    # 2. LangChain astream 으로 진짜 스트리밍
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.5, streaming=True)
    prompt = FINAL_ANSWER_PROMPT
    chain = prompt | llm | StrOutputParser()
    output_response = ""
    async for chunk in chain.astream({
        "is_relevant": is_relevant,
        "interest": interest,
        "education": education,
        "job_status": job_status,
        "location": location,
        "age": age,
        "chat_history": [],
        
        "user_message": user_message,
        "retrieved_docs": retrieved_docs,
        "web_docs": web_docs,
        "web_search_query": web_search_query,
        "final_context": [],
        "search_retry_count": 0,
    }):
        output_response += chunk
        yield chunk
        
    # 3. 멀티턴 memory 저장
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    chat_manager = ChatHistoryManager(user_id, room_id, llm)
    memory = chat_manager.get_memory_manager()
    memory.save_context(
        {"human": user_message},
        {"ai": output_response}
    )
