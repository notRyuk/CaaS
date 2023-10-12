import os
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
import jwt
from CaaS.config import JWT_ALGORITHM, JWT_SECRET_KEY, ROOTDIR
from fastapi.security import OAuth2PasswordBearer as Bearer
from CaaS.models.session import Session
from CaaS.models.user import User
from CaaS.utils.defaults import get_prefix
from typing import Annotated, List
from CaaS.core.rsa import RSAService
router = APIRouter(prefix=get_prefix("/test"))


@router.post("/upload")
async def index(
    token: Annotated[str, Depends(Bearer(tokenUrl="Bearer"))],
    file: UploadFile = File(...)
):
    res = {}
    rsa=RSAService()
    session = await Session.find_one({"token": token})
    
    try:
        session_data = jwt.decode(token, key=JWT_SECRET_KEY, algorithms=JWT_ALGORITHM)
    except Exception:
        await session.delete()
        return HTTPException(status_code=419, detail="Session expired please login again")
    
    session_data = jwt.decode(token, key=JWT_SECRET_KEY, algorithms=JWT_ALGORITHM)

    if not session_data["sub"] == session.email:
        return HTTPException(status_code=401, detail="Unauthorized!")
    user = await User.find_one({"email": session.email})
    path1 = os.path.join(ROOTDIR, str(user.id), "id_rsa.pub")
    path2 = os.path.join(ROOTDIR, str(user.id), "id_rsa")

    if not (os.path.isfile(path1) and os.path.isfile(path2)):
        status = rsa.generate_keys("id_rsa", str(user.id))
        if not status:
            return HTTPException(status_code=500, detail="Internal server error")
    
    print(rsa.get_base64(file.file.read()))
    
    
