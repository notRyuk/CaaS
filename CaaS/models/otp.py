from datetime import datetime
from beanie import Document

from CaaS.utils.models import Models

class Otp(Document):
    email: str
    signature: str
    createAt: datetime = datetime.now()

    class Settings:
        name = Models.otp
