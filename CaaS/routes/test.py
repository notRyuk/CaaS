from fastapi import APIRouter
from CaaS.utils.defaults import get_prefix
from CaaS.models.user import User

router = APIRouter(prefix=get_prefix("/test"))

@router.get("/")
async def index() -> dict:
    user = await (User(
        name="Test",
        email="test@gmail.com",
        phone="999999999",
        password="12344"
    )).insert()
    return {
        "data": "Test data",
        "user": user
    }