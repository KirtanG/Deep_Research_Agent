from exa_py import AsyncExa
from joblib import Memory
from langchain_core.messages import AIMessage, AnyMessage, HumanMessage

from app.core.config import get_settings

memory = Memory(location="./app/__pycache__")

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

#temporaraily cache the function to save api request credits
@memory.cache
async def search_exa(query:str,no_of_pages: int):
    settings = get_settings()
    exa_search = AsyncExa(api_key=settings.exa_api_key)

    result = await exa_search.search_and_contents(
        query=query,
        num_results=no_of_pages,
        highlights = True,
        
    )

    return result
