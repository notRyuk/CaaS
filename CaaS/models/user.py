from beanie import Document

class User(Document):
    name: str
    email: str
    phone: str
    password: str

    class Settings:
        name = "users"