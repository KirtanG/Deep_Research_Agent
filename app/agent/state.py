from operator import add
from typing import Annotated, Any, TypedDict

from langchain.messages import AnyMessage
from langgraph.graph.message import add_messages


class OverallState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    search_query: Annotated[list[str], add]
    web_research_result: Annotated[list[Any], add]  # pyright: ignore[reportExplicitAny]
    sources_gathered: Annotated[list[Any], add] # pyright: ignore[reportExplicitAny]
    initial_search_query_count: int
    max_research_loops: int
    research_loop_count: int
    reasoning_model: str

class ReflectionState(TypedDict):
    is_sufficient: bool
    knowledge_gap: str
    follow_up_queries: Annotated[list[str], add]
    research_loop_count: int
    number_of_ran_queries: int

class Query(TypedDict):
    query: str
    rationale: str

class QueryGenerationState(TypedDict):
    search_query: list[Query]

class WebSearchState(TypedDict):
    search_query: str
    id: str