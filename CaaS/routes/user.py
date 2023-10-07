import logging
from datetime import datetime, timedelta

import jwt
from fastapi import APIRouter, HTTPException

from CaaS.models import User
from CaaS.models import Session
from CaaS.utils.defaults import get_prefix
from pydantic import BaseModel

router = APIRouter(prefix=get_prefix("/user"))
logger = logging.getLogger("uvicorn.info")


class LoginUser(BaseModel):
    email: str
    password: str


@router.post("/login")
async def login(user: LoginUser):
    existing_user = await User.find_one({"email": user.email})
    if existing_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if user.password != existing_user.password:
        raise HTTPException(status_code=401, detail="Incorrect password")

    # Create a payload for the JWT token
    token_data = {"sub": existing_user.email}
    access_token = create_access_token(token_data)

    session = Session(
        created_at=datetime.now(),
        user=str(existing_user.id),  # Replace with the user's ID
        token=access_token  # Replace with the user's access token
    )    # Generate a JWT token

    await session.insert()

    return {"access_token": access_token, "token_type": "bearer"}


SECRET_KEY = "CloudComputing"  # Replace with your actual secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Set your desired token expiration time


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@router.post("/signup")
async def signup(user: User):
    existing_user = await User.find_one({'email': user.email})
    logger.info(existing_user)
    if existing_user:
        return HTTPException(status_code=400, detail="User with this email already exists")
    new_user = User(
        name=user.name,
        email=user.email,
        phone=user.phone,
        password=user.password
    )
    await new_user.insert()
    return {"message": "Signup successful"}
