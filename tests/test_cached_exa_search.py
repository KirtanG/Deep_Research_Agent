import asyncio

from joblib import Memory

from app.agent.utils import search_exa

memory = Memory(location="./app/__pycache__")

@memory.cache
async def main() -> None:
    query = "Gemini 2.5 deprecation"

    response = await search_exa(query=query,no_of_pages=5)

    #rint(type(results))
    #print(results)
    for result in response.results:
       print("===== Exa Results =====")
       print(type(result))
       print(result.title)
       print(result.url)
       print(result.highlights)
       print(result.text)
       print(result.published_date)
       print("END")


if __name__ == "__main__":
    asyncio.run(main())