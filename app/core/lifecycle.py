import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None,Any]:  # pyright: ignore[reportExplicitAny]
    """This function handles the startup and Shutdown Events."""
    logger.info("Starting the API server...")
    yield 
    logger.info("Shutting the server down...")    

