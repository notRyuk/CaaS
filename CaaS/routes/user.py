import logging
import os
from datetime import datetime, timedelta
from typing import Annotated

import jwt
from Crypto.Random import random
from fastapi import APIRouter, Form, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel

from CaaS.config import JWT_ALGORITHM as ALGORITHM
from CaaS.config import JWT_SECRET_KEY as SECRET_KEY
from CaaS.core.dsa import DSAService
from CaaS.models import Otp, Session, User
from CaaS.models.user import Otp as UserOtp
from CaaS.utils import mailer
from CaaS.utils.defaults import get_prefix

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
    
    dsaService=DSAService()
    otp=random.randrange(100000,1000000)
    sign = dsaService.encrypting(email=user.email, id=str(existing_user.id), otp=otp)
    ootp = Otp(email=existing_user.email, signature=sign)
    await ootp.insert()
    mailer.sendMail(user.email, f"Your OTP for getting your files fked is <b>{otp}</b>")
    return {"message": "Login successful", "email": existing_user.email}




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
    otp = random.randrange(100000, 1000000)

    new_user = User(
        name=user.name,
        email=user.email,
        phone=user.phone,
        password=user.password,
        otp=UserOtp(verified=False, otp=otp)
    )
    mailer.sendMail(user.email, f"Your OTP for getting your files fked is <b>{otp}</b>")
    await new_user.insert()
    return {"message": "OTP sent to the registered email."}

class OTP(BaseModel):
    email: str
    otp: int

class TempFileResponse(FileResponse):
    def __init__(self, path: str):
        super().__init__(path)

    def __del__(self):
        os.remove(self.path)

@router.post("/signupotp")
async def verify_signup(otp_user: OTP):
    existing_user = await User.find_one({'email': otp_user.email})
    if not existing_user:
        return HTTPException(status_code=404, detail="User not found")
    dsaService = DSAService()
    dsaService.generate_keys(str(existing_user.id), existing_user.email)
    del existing_user.otp
    await existing_user.save()
    path = os.path.join(os.getcwd(), "temp", str(existing_user.id), "id_dsa")
    res = TempFileResponse(path)
    return res
    

    

@router.post("/loginotp")
async def verify_login(otp_user: Annotated[OTP, Form()], file: bytes = File(...)):
    print(file) 
    usr = await User.find_one({"email": otp_user.email})
    if not usr:
        return HTTPException(status_code=404, detail="User not found")
    ootp = await Otp.find_one({"email": usr.email})
    if not ootp:
        return HTTPException(status_code=403, detail="Unauthorized")
    dsaService = DSAService()
    verified = dsaService.decrypting(otp_user.email, str(usr.id), otp_user.otp, ootp.signature)
    if not verified:
        return HTTPException(status_code=403, detail="Invalid Otp.")
    token_data = {"sub": usr.email}
    access_token = create_access_token(token_data)
    session = Session(
        created_at=datetime.now(),
        email=usr.email,
        token=access_token
    )
    await session.insert()
    await ootp.delete()
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/test")
async def test():
    service = DSAService()
    sign = service.encrypting("dattasandeep000@gmailcom", "65230ef8f46d005d372ab08d", 1)
    print(sign)
    verfied = service.decrypting("dattasandeep000@gmail.com", "65230ef8f46d005d372ab08d", 1, sign)
    return verfied
