from fastapi import FastAPI
from .routes import detect

app = FastAPI(title="GayBuster API")

from .startup import *  # noqa

app.include_router(detect.router, prefix="/detect")
