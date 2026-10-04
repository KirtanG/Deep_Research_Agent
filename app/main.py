#!/usr/bin/python3

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from app.core.config import get_settings

settings = get_settings()  

app: FastAPI = FastAPI()

@app.get("/")
def health()  -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content="Ok"
    )
