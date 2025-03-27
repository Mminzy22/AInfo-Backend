from datetime import datetime

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableMap
from langchain_openai import ChatOpenAI

from chatbot.langchain_flow.prompts.detail_rag_prompt import DETAIL_RAG_PROMPT
from chatbot.langchain_flow.tools.detail_rag_tool import detail_rag_tool
from chatbot.langchain_flow.tools.tavily_web_tool import tavily_web_search_tool

llm = ChatOpenAI(model="gpt-4o", temperature=0.5, streaming=True)
current_date = datetime.now()
current_year_month = f"{current_date.year}년 {current_date.month}월"


DETAIL_CHAIN = (
    RunnableMap(
        {
            "question": lambda x: x["question"],
            "context": lambda x: detail_rag_tool.run(
                {"query": " ".join(x["keywords"])}
            ),
            "web_search": lambda x: tavily_web_search_tool.invoke(
                {
                    "query": " ".join(x["keywords"]),
                    "k": x.get("k", 4),  # 'k'를 외부 입력에서 받거나 기본값 4
                }
            ),
            "current_year_month": lambda _: current_year_month,
            "chat_history": lambda x: x.get("chat_history", []),
        }
    )
    | DETAIL_RAG_PROMPT
    | llm
    | StrOutputParser()
)
