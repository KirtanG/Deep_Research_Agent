import asyncio

from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig

from app.agent.nodes import generate_query
from app.agent.state import OverallState


async def main():
    # 1. Prepare sample state
    state: OverallState = {
        "messages": [HumanMessage(content="When will be gemini 2.5 flash deprecated")],
        "search_query": [],
        "web_research_result": [],
        "sources_gathered": [],
        "initial_search_query_count": 3,
        "max_research_loops": 1,
        "research_loop_count": 0,
        "reasoning_model": "gemini-3.5-flash",
    }

    # 2. Prepare configuration
    config: RunnableConfig = {
        "configurable": {
            "query_generator_model": "gemini-3.1-flash-lite", # or your configured model
            "number_of_initial_queries": 3,
        }
    }

    # 3. Invoke the node
    result = await generate_query(state, config)
    print("Generated Query State:", result)


if __name__ == "__main__":
    asyncio.run(main())
