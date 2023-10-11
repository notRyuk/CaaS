import os
from fastapi import APIRouter, File, UploadFile

from CaaS.models.user import User
from CaaS.utils.defaults import get_prefix
from typing import List

router = APIRouter(prefix=get_prefix("/test"))


@router.post("/upload")
async def index(file: UploadFile = File(...)):
    res = {}
    try:
        with open(os.path.join(os.getcwd(), "temp", file.filename), "wb") as f:
            f.write(file.file.read())
        res[file.filename] = "Saved"
    except Exception:
        res[file.filename] = "Not saved"
    finally:
        file.file.close()
    return res
