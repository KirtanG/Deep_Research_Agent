from datetime import datetime

from langchain.chat_models import init_chat_model
from langchain.messages import AIMessage
from langchain_core.runnables import RunnableConfig
from langgraph.types import Send

from app.agent.configuration import Configuration
from app.agent.prompts import (
    answer_instructions,
    get_current_date,
    query_writer_instructions,
    reflection_instructions,
    web_summariser_instructions,
)
from app.agent.schemas import Reflection, SearchQueryList
from app.agent.state import (
    OverallState,
    QueryGenerationState,
    ReflectionState,
    WebSearchState,
)
from app.agent.utils import get_research_topic, search_exa
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

    search_query_generator = init_chat_model(
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

async def web_research(state: WebSearchState, config: RunnableConfig) -> OverallState: 
    """LangGraph node that performs web research using the native Google Search API tool.

    Executes a web search using the native Google Search API tool in combination with Gemini 2.0 Flash.

    Args:
        state: Current graph state containing the search query and research loop count
        config: Configuration for the runnable, including search API settings

    Returns:
        Dictionary with state update, including sources_gathered, research_loop_count, and web_research_results
    """
    configurable = Configuration.from_runnable_config(config)
    settings = get_settings()

    current_date = get_current_date()

    response = await search_exa(state["search_query"],configurable.number_of_pages)
    
    extracted_results = []
    sources_gathered = []
    source_content = []

    for result in response.results:
        raw_date = result.published_date

        parsed_date = None
        if raw_date:
            try:
                # Normalize standard ISO strings
                parsed_date = datetime.fromisoformat(raw_date.replace("Z", "+00:00"))  # noqa: FURB162
            except (ValueError, TypeError):
                pass
        
        extracted_results.append({
            "url": result.url,
            "text": result.text,
            "title": result.title,
            "published_date": parsed_date
        })

    extracted_results.sort(
        key=lambda x: (
            x["published_date"] is not None, 
            x["published_date"] if x["published_date"] else datetime.min
        ),
        reverse=True
    )


    for index, result in enumerate(extracted_results):
        short_url = f"[{state['id']}-{index}]"

        sources_gathered.append({
            "short_url": short_url,
            "value": f"{result['url']}"
        })
    
        date_str = result["published_date"].strftime("%Y-%m-%d") if result["published_date"] else "Unmarked/Unknown"

        source_content.append(
            f"ID: {short_url}\n"
            f"URL: {result['url']}\n"
            f"Date: {date_str}\n"
            f"Content:\n{result['text']}"
        )
        
    content = "\n\n".join(source_content)

    summary_llm_prompt = web_summariser_instructions.format(
        research_topic=state["search_query"],
        current_date=current_date,
        sources=content
    )
    
    summary_llm = init_chat_model(
        model = configurable.query_generator_model,
        temperature = 1.0,
        api_key = settings.google_api_key
    )

    summary = await summary_llm.ainvoke(input=summary_llm_prompt)
    
    return { 
        "sources_gathered": sources_gathered, 
        "search_query":[state["search_query"]],
        "web_research_result" : [summary.text]
    }


async def reflection(state: OverallState, config: RunnableConfig) -> ReflectionState:
    """LangGraph node that identifies knowledge gaps and generates potential follow-up queries.

    Analyzes the current summary to identify areas for further research and generates
    potential follow-up queries. Uses structured output to extract
    the follow-up query in JSON format.

    Args:
        state: Current graph state containing the running summary and research topic
        config: Configuration for the runnable, including LLM provider settings

    Returns:
        Dictionary with state update, including search_query key containing the generated follow-up query
    """
    configurable = Configuration.from_runnable_config(config)
    settings = get_settings()
    current_date = get_current_date()

    state["research_loop_count"] = state.get("research_loop_count", 0) + 1

    formatted_reflection_prompt = reflection_instructions.format(
        current_date = current_date,
        research_topic = get_research_topic(state['messages']),
        summaries = "\n\n---\n\n".join(state["web_research_result"])
    )

    reflection_llm = init_chat_model(
        model = configurable.reflection_model,
        temperature = 1.0,
        max_retries = 3,
        api_key = settings.google_api_key
    )

    structured_reflection_llm = reflection_llm.with_structured_output(Reflection)

    result = await structured_reflection_llm.ainvoke(formatted_reflection_prompt)  # pyright: ignore[reportAssignmentType]

    return {
        "is_sufficient": result.is_sufficient,
        "knowledge_gap": result.knowledge_gap,
        "follow_up_queries": result.follow_up_queries,
        "research_loop_count": state["research_loop_count"],
        "number_of_ran_queries": len(state["search_query"]),    
    }

def evaluate_research(
    state: ReflectionState,
    config: RunnableConfig,
) -> OverallState:
    """LangGraph routing function that determines the next step in the research flow.

    Controls the research loop by deciding whether to continue gathering information
    or to finalize the summary based on the configured maximum number of research loops.

    Args:
        state: Current graph state containing the research loop count
        config: Configuration for the runnable, including max_research_loops setting

    Returns:
        String literal indicating the next node to visit ("web_research" or "finalize_summary")
    """
    configurable = Configuration.from_runnable_config(config)
    max_research_loops = (
        state.get("max_research_loops")
        if state.get("max_research_loops") is not None
        else configurable.max_research_loops
    )
    if state["is_sufficient"] or state["research_loop_count"] >= max_research_loops:
        return "finalize_answer"
    else:
        return [
            Send(
                "web_research",
                {
                    "search_query": follow_up_query,
                    "id": state["number_of_ran_queries"] + int(idx),
                },
            )
            for idx, follow_up_query in enumerate(state["follow_up_queries"])
        ]

async def finalise_answer(state: OverallState, config: RunnableConfig) -> OverallState:
    """LangGraph node that finalizes the research summary.

    Prepares the final output by deduplicating and formatting sources, then
    combining them with the running summary to create a well-structured
    research report with proper citations.

    Args:
        state: Current graph state containing the running summary and sources gathered

    Returns:
        Dictionary with state update, including running_summary key containing the formatted final summary with sources
    """
    configurable = Configuration.from_runnable_config(config)
    settings = get_settings()
    current_date = get_current_date()

    answer_prompt = answer_instructions.format(
            current_date = current_date,
            research_topic = get_research_topic(state['messages']),
            summaries = "\n\n---\n\n".join(state["web_research_result"])
        )
    
    answer_llm = init_chat_model(
        model = configurable.reflection_model,
        temperature = 0,
        max_retries = 3,
        api_key = settings.google_api_key
    )

    result = await answer_llm.ainvoke(answer_prompt)

    # Replace the short urls with the original urls and add all used urls to the sources_gathered
    unique_sources = []
    for source in state["sources_gathered"]:
        if source["short_url"] in result.content:
            result.content = result.content.replace(
                source["short_url"], source["value"]
            )
            unique_sources.append(source)

    return {
        "messages": [AIMessage(content=result.content)],
        "sources_gathered": unique_sources,
    }

