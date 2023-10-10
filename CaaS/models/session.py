from datetime import datetime

from beanie import Document

from CaaS.utils.models import Models


class Session(Document):
    created_at: datetime
    email: str
    token: str

    class Settings:
        name = Models.session
