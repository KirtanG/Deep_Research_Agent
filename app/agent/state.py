from operator import add
from typing import Annotated, Any, TypedDict

from langchain.messages import AnyMessage
from langgraph.graph import add_messages


class OverallState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    search_query: Annotated[list[str], add]
    web_research_result: Annotated[list[Any], add]  # pyright: ignore[reportExplicitAny]
    sources_gathered: Annotated[list[Any], add] # pyright: ignore[reportExplicitAny]
    initial_search_query_count: int
    max_research_loops: int
    research_loop_count: int
    reasoning_model: str