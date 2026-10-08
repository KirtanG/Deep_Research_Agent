from langchain_core.runnables import RunnableConfig
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from langgraph.types import Send

from app.agent.configuration import Configuration
from app.agent.prompts import (
    get_current_date,
    query_writer_instructions,
    web_searcher_instructions,
)
from app.agent.schemas import SearchQueryList
from app.agent.state import OverallState, QueryGenerationState, WebSearchState
from app.agent.utils import get_research_topic
from app.core.config import get_settings


async def generate_query(state: OverallState, config: RunnableConfig) -> QueryGenerationState:
    """LangGraph node that generates search queries based on the User's question.

    Uses Gemini 2.0 Flash to create an optimized search queries for web research based on
    the User's question.

    Args:
        state: Current graph state containing the User's question
        config: Configuration for the runnable, including LLM provider settings

    Returns:
        Dictionary with state update, including search_query key containing the generated queries
    """

    configurable = Configuration.from_runnable_config(config)
    settings = get_settings()

    if state.get("initial_search_query_count") is None:
        state['initial_search_query_count'] = configurable.number_of_initial_queries

    search_query_generator = ChatGoogleGenerativeAI(
        model = configurable.query_generator_model,
        temperature = 1.0,
        max_retries = 3,
        api_key = settings.google_api_key
    )

    structured_query_generator = search_query_generator.with_structured_output(SearchQueryList)

    current_date = get_current_date()

    query_writer_formatted_prompt = query_writer_instructions.format(
        current_date=current_date,
        number_queries=state["initial_search_query_count"],
        research_topic=get_research_topic(state["messages"])
    )

    result = await structured_query_generator.ainvoke(query_writer_formatted_prompt)

    generated_queries_state = QueryGenerationState(
        search_query = result.query
    )

    return generated_queries_state 

def continue_to_web_research(state: QueryGenerationState)-> list[Send]:
    """LangGraph node that sends the search queries to the web research node.

    This is used to spawn n number of web research nodes, one for each search query.
    """

    return [
        Send("web_research", {"search_query":search_query, "id": int(idx)})
        for idx,search_query in enumerate(state["search_query"])
    ]

def web_research(state: WebSearchState, config: RunnableConfig) -> None:

    configurable = Configuration.from_runnable_config(config)

    current_date = get_current_date()
