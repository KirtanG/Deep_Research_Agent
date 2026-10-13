#!/usr/bin/python3
import logging

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from app.core.lifecycle import lifespan
from app.core.logging import setup_logging

setup_logging(log_level="INFO")

logger = logging.getLogger(__name__)

app: FastAPI = FastAPI(lifespan=lifespan)

@app.get("/")
def health()  -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content="Ok"
    )
