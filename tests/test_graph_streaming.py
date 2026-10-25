import asyncio

from langchain.messages import HumanMessage
from langchain_core.runnables import RunnableConfig

from app.agent.state import OverallState
from app.agent.graph import graph


async def main():
    state: OverallState = {
        "messages": [HumanMessage(content="When will be gemini 2.5 flash deprecated?")],
        "search_query": [],
        "web_research_result": [],
        "sources_gathered": [],
        "initial_search_query_count": 3,
        "max_research_loops": 3,
        "research_loop_count": 0,
        "reasoning_model": "gemini-2.5-flash",
    }

    # 2. Prepare configuration
    config: RunnableConfig = {
        "configurable": {
            "query_generator_model":"google_genai:gemini-2.5-flash",
            "reflection_model":"google_genai:gemini-2.5-flash",
            "answer_model":"google_genai:gemini-3-flash",
            "number_of_pages":10,
            "max_research_loops":3,
            "number_of_initial_queries": 3,
        }
    }

    async for chunk in graph.astream(input = state,config = config,stream_mode=["updates"]):
        print(chunk)




if __name__ == "__main__":
    asyncio.run(main())