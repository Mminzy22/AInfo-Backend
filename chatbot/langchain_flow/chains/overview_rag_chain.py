from langchain_core.runnables import RunnableMap
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from chatbot.langchain_flow.prompts.overview_rag_prompt import OVERVIEW_RAG_PROMPT
from chatbot.langchain_flow.tools.overview_rag_tool import overview_rag_tool

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.5, streaming=True)

OVERVIEW_CHAIN = (
    RunnableMap(
        {
            "question": lambda x: x["question"],
            "context": lambda x: overview_rag_tool.run(
                {"query": " ".join(x["keywords"])}
            ),
            "chat_history": lambda x: x.get("chat_history", []),
        }
    )
    | OVERVIEW_RAG_PROMPT
    | llm
    | StrOutputParser()
)
