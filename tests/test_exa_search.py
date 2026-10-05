import asyncio

from app.agent.utils import search_exa


async def main() -> None:
    query = "AWS ElasticCache"

    results = await search_exa(query=query)

    print(results)

if __name__ == "__main__":
    asyncio.run(main())