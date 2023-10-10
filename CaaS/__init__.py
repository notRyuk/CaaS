import logging

from beanie import init_beanie
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

from CaaS.config import DB_URL
from CaaS.models import __all__ as ALL_MODELS
from CaaS.routes import test, user

app = FastAPI()
logger = logging.getLogger("uvicorn.info")

app.include_router(test.router)
app.include_router(user.router)


async def connect():
    client = AsyncIOMotorClient(DB_URL)
    await init_beanie(
        database=client.CaaS_Test,
        document_models=ALL_MODELS
    )
    logger.info("Connected to the database")
