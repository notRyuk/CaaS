from fastapi import APIRouter, File, Depends, HTTPException
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer as Bearer
from CaaS.models import Session, User
from fastapi.responses import FileResponse
import jwt, os
from CaaS.config import JWT_SECRET_KEY, JWT_ALGORITHM


router = APIRouter(prefix="/static")

@router.get("/{file}")
async def get_file(
    file: str, 
    token: Annotated[str, Depends(Bearer(tokenUrl="Bearer"))]
):
    if file.endswith(".encrypted"):
        return HTTPException(status_code=404, detail="Invalid URL")
    session = await Session.find_one({"token": token})
    try:
        session_data = jwt.decode(token, key=JWT_SECRET_KEY, algorithms=JWT_ALGORITHM)
    except Exception:
        await session.delete()
        return HTTPException(status_code=419, detail="Session expired please login again")
    
    if not session_data["sub"] == session.email:
        return HTTPException(status_code=401, detail="Unauthorized!")
    user = await User.find_one({"email": session.email})
    path = os.path.join(os.getcwd(), "temp", str(user.id), file)
    if not os.path.isfile(path):
        return HTTPException(status_code=404, detail="<h1>404 Bad Request! File not found</h1>")
    return FileResponse(path)