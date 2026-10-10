import asyncio

from app.agent.nodes import web_research
from app.agent.state import WebSearchState


async def main():
    config: RunnableConfig = {
        "configurable": {
            "query_generator_model": "gemini-3.1-flash-lite", # or your configured model
            "number_of_initial_queries": 3,
            "number_of_pages":5
        }
    }

    web_research_state : WebSearchState = {
        "id":1,
        "search_query":"Gemini 2.5 deprecation"
    }

    result = await web_research(state=web_research_state,config = config)
    
    print(result)
    



if __name__ == "__main__":
    asyncio.run(main())