from fastapi import FastAPI
from CaaS.routes import test

app = FastAPI()

app.include_router(test.router)

