from fastapi import APIRouter
from CaaS.utils.defaults import get_prefix
from CaaS.models.user import User

router = APIRouter(prefix=get_prefix("/test"))


@router.get("/")
async def index() -> dict:
    return {
        "data": "Test data"
    }
