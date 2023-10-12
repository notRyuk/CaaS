from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.security import OAuth2PasswordBearer as Bearer
from fastapi.responses import FileResponse
from typing import Annotated
from CaaS.utils.defaults import get_prefix
from CaaS.models import Session, File as File_, User
from CaaS.config import JWT_SECRET_KEY, JWT_ALGORITHM, ROOTDIR
from CaaS.core.rsa import RSAService, EncryptionData
import jwt, os

router = APIRouter(prefix=get_prefix("/files"))

@router.get("/get")
async def get_files(token: Annotated[str, Depends(Bearer(tokenUrl="Bearer"))]):
    session = await Session.find_one({"token": token})
    try:
        session_data = jwt.decode(token, key=JWT_SECRET_KEY, algorithms=JWT_ALGORITHM)
    except Exception:
        await session.delete()
        return HTTPException(status_code=419, detail="Session expired please login again")

    if not session_data["sub"] == session.email:
        return HTTPException(status_code=401, detail="Unauthorized!")
    files = await File_.find({"email": session.email}).to_list()
    if not files:
        return []
    return files


@router.post("/upload")
async def upload_file(token: Annotated[str, Depends(Bearer(tokenUrl="Bearer"))], file: UploadFile = File(...)):
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
    dir = os.path.join(ROOTDIR, str(user.id))
    ed = rsa.encrypt(file.file.read().decode(), "id_rsa.pub", "pk", root=dir)
    print(ed)
    with rsa.write_file(file.filename+".encrypted", "wb", dir) as f:
        [f.write(rsa.get_bytes(ed[x])) for x in (
            "secret_token",
            "nonce",
            "tag",
            "ct"
        )]
    fd = File_(email=user.email, file=file.filename)
    await fd.insert()
    return fd

class TempFileResponse(FileResponse):
    def __init__(self, path: str, *args, **kwargs):
        super().__init__(path, *args, **kwargs)

    def __del__(self):
        os.remove(self.path)

@router.get("/download/{filename}")
async def download_file(filename:str, token: Annotated[str, Depends(Bearer(tokenUrl="Bearer"))]):
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
    if not user:
        return HTTPException(status_code=403, detail="Unauthorized!")
    
    rsa = RSAService()
    if not rsa.is_file(filename+".encrypted", os.path.join(ROOTDIR, str(user.id))):
        return HTTPException(status_code=404, detail="Bad Request! No such file exists")
    
    path1 = os.path.join(ROOTDIR, str(user.id), "id_rsa.pub")
    path2 = os.path.join(ROOTDIR, str(user.id), "id_rsa")
    print((os.path.isfile(path1) and os.path.isfile(path2)))
    if not (os.path.isfile(path1) and os.path.isfile(path2)):
        return HTTPException(status_code=500, detail="Internal server error")
    
    fd = rsa.read_file(filename+".encrypted", "rb", os.path.join(ROOTDIR, str(user.id)))
    ed: EncryptionData = {"key_type": "pk"}
    ed["secret_token"], ed["nonce"], ed["tag"], ed["ct"] = [rsa.get_base64(fd.read(x)) for x in (256, 16, 16, -1)]
    print(ed)
    data = rsa.decrypt(ed, "id_rsa", root=os.path.join(ROOTDIR, str(user.id)))
    if not data:
        return HTTPException(status_code=500, detail="Internal server error")
    rsa.write_file(filename, "wb", os.path.join(os.getcwd(), "temp")).write(data.encode())
    return TempFileResponse(
        os.path.join(os.getcwd(), "temp", filename), 
        headers={
            "content-disposition": filename
        }, 
        filename=filename
    )
