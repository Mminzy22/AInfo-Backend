from typing import Optional

from langchain.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults
from pydantic import BaseModel, Field

tavily = TavilySearchResults(k=4)


class TavilySearchInput(BaseModel):
    query: str = Field(..., description="The search query string")
    k: Optional[int] = Field(
        4, description="Number of search results to return (default is 4)."
    )


@tool("tavily_web_search_tool", args_schema=TavilySearchInput)
def tavily_web_search_tool(query: str, k: Optional[int] = 4) -> str:
    """
    A web search tool using Tavily.
    Useful for retrieving up-to-date information from the web.
    """
    search_tool = TavilySearchResults(k=k)
    return search_tool.run(query)
