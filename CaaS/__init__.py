import logging
from fastapi import FastAPI
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
import CaaS.models as models
from CaaS.config import DB_URL

from CaaS.routes import test, user

app = FastAPI()
logger = logging.getLogger("uvicorn.info")

app.include_router(test.router)
app.include_router(user.router)

async def connect():
    client = AsyncIOMotorClient(DB_URL)
    await init_beanie(
        database=client.CaaS_Test,
        document_models=models.__all__
    )
    logger.info("Connected to the database")
