from fastapi import APIRouter
from CaaS.utils.defaults import get_prefix
from pydantic import BaseModel

router = APIRouter(prefix=get_prefix("/user"))

class LoginUser(BaseModel):
    email: str
    password: str

@router.post("/login")
async def login(user: LoginUser):
    pass