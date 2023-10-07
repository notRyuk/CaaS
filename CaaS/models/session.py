from datetime import datetime
from beanie import Document
from CaaS.utils.models import Models
from CaaS.utils.objectid import ObjectId


class Session(Document):
    created_at: datetime
    user: str
    token: str

    class Settings:
        name = Models.session
