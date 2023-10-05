from fastapi import APIRouter
from CaaS.utils.defaults import get_prefix

router = APIRouter(prefix=get_prefix("/user"))