from exa_py import AsyncExa
from langchain_core.messages import AIMessage, AnyMessage, HumanMessage

from app.main import settings


def get_research_topic(messages: list[AnyMessage]) -> str:
    """
    Get the research topic from the messages.
    """
    # check if request has a history and combine the messages into a single string
    if len(messages) == 1:
        research_topic = messages[-1].content
    else:
        research_topic = ""
        for message in messages:
            if isinstance(message, HumanMessage):
                research_topic += f"User: {message.content}\n"
            elif isinstance(message, AIMessage):
                research_topic += f"Assistant: {message.content}\n"
    return research_topic

async def search_exa(query:str):
    exa_search = AsyncExa(api_key=settings.exa_api_key)

    result = await exa_search.search(
        query=query,
        num_results=10
    )

    return result