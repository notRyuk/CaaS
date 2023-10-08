from datetime import datetime
from typing import Optional
from beanie import Document
from pydantic import BaseModel
from CaaS.utils.models import Models

class Otp(BaseModel):
    verified: bool
    createdAt: datetime = datetime.now()
    otp: int

class User(Document):
    name: str
    email: str
    phone: str
    password: str
    otp: Otp = None

    class Settings:
        name = Models.user

       