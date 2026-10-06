import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI

from app.core.config import get_settings
from app.services.crawl_4_ai import Crawl4AIService, get_browser_config

logger = logging.getLogger(__name__)

crawler_service = Crawl4AIService(get_browser_config(get_settings()))

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None,Any]:  # pyright: ignore[reportExplicitAny]
    """This function handles the startup and Shutdown Events."""
    logger.info("Starting the API server...")
    await crawler_service.start()
    yield
    await crawler_service.close()
    logger.info("Shutting the server down...")    
