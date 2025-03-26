from typing import Optional

from langchain.tools import tool
from pydantic import BaseModel, Field

from chatbot.retriever import VectorRetriever


class RAGsearchInput(BaseModel):
    query: str = Field(..., description="Question or keywords to search for")
    k: Optional[int] = Field(
        3, description="Number of documents to retrieve per collection"
    )
    filters: Optional[dict] = Field(
        None, description="Metadata filters for document retrieval"
    )


@tool("overview_rag_tool", args_schema=RAGsearchInput)
def overview_rag_tool(
    query: str,
    k: int = 3,
    filters: Optional[dict] = None,
) -> str:
    """
    Perform similarity-based document retrieval from multiple Chroma collections
    and returns the results as a formatted string.

    Extracts policy-related documents based on the given search query
    """

    collection_names = [
        "gov24_service_list",
        "youth_policy_list",
        "employment_programs",
        "pdf_sections",
    ]

    retriever = VectorRetriever()
    docs = retriever.search(
        query=query, k=k, filters=filters, collection_names=collection_names
    )
    return retriever.format_docs(docs)
