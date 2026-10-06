#!/usr/bin/python3

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from app.core.lifecycle import lifespan

app: FastAPI = FastAPI(lifespan=lifespan)

@app.get("/")
def health()  -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content="Ok"
    )
