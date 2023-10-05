from fastapi import APIRouter
from CaaS.utils.defaults import get_prefix

router = APIRouter(prefix=get_prefix("/test"))

@router.get("/")
def index() -> dict:
    return {
        "data": "Test data"
    }