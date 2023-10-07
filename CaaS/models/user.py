from beanie import Document
from CaaS.utils.models import Models


class User(Document):
    name: str
    email: str
    phone: str
    password: str

    class Settings:
        name = Models.user
