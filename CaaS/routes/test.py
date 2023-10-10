from fastapi import APIRouter

from CaaS.models.user import User
from CaaS.utils.defaults import get_prefix

router = APIRouter(prefix=get_prefix("/test"))


@router.get("/")
async def index() -> dict:
    return {
        "data": "Test data"
    }
