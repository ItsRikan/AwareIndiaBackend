import os
import uuid

from fastapi import APIRouter, UploadFile,File
from fastapi.responses import JSONResponse
from imagekitio import ImageKit
from dotenv import load_dotenv

load_dotenv() 

router = APIRouter(
    prefix="/imagekit",
    tags=["imagekit"]
)

IMAGEKIT_PUBLIC_KEY = os.getenv("IMAGEKIT_PUBLIC_KEY")
IMAGEKIT_URL_ENDPOINT = os.getenv("IMAGEKIT_URL_ENDPOINT")
IMAGEKIT_PRIVATE_KEY = os.getenv("IMAGEKIT_PRIVATE_KEY")
if not IMAGEKIT_PRIVATE_KEY:
    raise RuntimeError("IMAGEKIT_PRIVATE_KEY not set in env")

imagekit = ImageKit(private_key=IMAGEKIT_PRIVATE_KEY)

@router.get("/auth")
async def imagekit_auth():
    token = uuid.uuid4().hex
    auth = imagekit.helper.get_authentication_parameters(token=token)
    return JSONResponse(
        {
            "signature": auth["signature"],
            "token": auth["token"],
            "expire": auth["expire"],
            "publicKey": IMAGEKIT_PUBLIC_KEY,
            "urlEndpoint": IMAGEKIT_URL_ENDPOINT,
        }
    )


@router.get("/upload")
async def imagekit_upload(file:UploadFile=File(...)):
    file_content = await file.read()
    otions = imagekit.files.    x   
    response = imagekit.files.upload(file=file_content,file_name=file.filename,use_unique_file_name=True)
    return {"url":response.url}


