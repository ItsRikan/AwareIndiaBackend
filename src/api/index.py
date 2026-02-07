from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uuid
from pydantic import BaseModel,Field
import time
import random

from src.routers import imagekit_auth,auth,scan,history

app = FastAPI()

origins = ["*","http://localhost:8080/"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(imagekit_auth.router)
app.include_router(scan.router)
app.include_router(auth.router)
app.include_router(history.router)

@app.get('/')
async def health_check():
    return {'status':'healthy'}



