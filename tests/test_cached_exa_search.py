import asyncio

from joblib import Memory

from app.agent.utils import search_exa

memory = Memory(location="./app/__pycache__")

@memory.cache
async def main() -> None:
    query = "Gemini 2.5 deprecation"

    results = await search_exa(query=query)

    print(results)

if __name__ == "__main__":
    asyncio.run(main())