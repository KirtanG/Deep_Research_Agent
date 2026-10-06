from crawl4ai import AsyncWebCrawler, BrowserConfig

from app.core.config import Settings


def get_browser_config(settings: Settings) -> BrowserConfig:
    if settings.crawler_mode == "cdp":
        return BrowserConfig(browser_mode="cdp", cdp_url=settings.crawler_cdp_url)
    return BrowserConfig(browser_mode="builtin")


class Crawl4AIService:

    def __init__(self,browser_config: BrowserConfig)-> None:
        self._browser_config: BrowserConfig =browser_config
        self._crawler: AsyncWebCrawler | None = None

    async def start(self) -> None:
        self._crawler = AsyncWebCrawler(config=self._browser_config)
        await self._crawler.start()   
    
    async def close(self) -> None:
        if self._crawler is not None:
            await self._crawler.close()
            self._crawler = None

    async def fetch(self, url: str) -> str | None:
        if self._crawler is None:
            raise RuntimeError("CrawlerService not started — call start() first")
        result = await self._crawler.arun(url=url)  
        return result.markdown
        
