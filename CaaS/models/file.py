from datetime import datetime

from beanie import Document

from CaaS.utils.models import Models


class File(Document):
    email: str
    file: str
    createAt: datetime = datetime.now()

    class Settings:
        name = Models.file
