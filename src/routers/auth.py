import os

from fastapi import APIRouter, HTTPException, Header, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from supabase.client import create_client
from supabase_auth.errors import AuthApiError
from src.schema import (
    SignupSchema,
    LoginSchema,
    RefreshTokenRequest,
    RefreshTokenResponse,
    ConfirmRequest
    )

load_dotenv()

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

supabase_api_key = os.getenv("SUPABASE_API_KEY")
supabase_url = os.getenv("SUPABASE_PROJECT_URL")

supabase = create_client(supabase_url=supabase_url,supabase_key=supabase_api_key)
security = HTTPBearer()


def get_current_user(creds:HTTPAuthorizationCredentials=Depends(security)):
    token = creds.credentials
    try:
        user = supabase.auth.get_user(token)
        return user.user
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )


@router.post("/sign_up")
async def sign_up(data:SignupSchema):
    res = supabase.auth.sign_up(
        {
        "email": data.email,
        "password": data.password,
        "options": {
            "data": {
                "name": data.name
            }
        }
    })
    if not res.user:
        raise HTTPException(status_code=400, detail="signup failed")
    
    if not getattr(res, "session", None) or not getattr(res.session, "access_token", None):
        return {
            "message": "Confirmation required. Check your email and confirm before logging in.",
            "user_id": res.user.id
        }
    return {
        "access_token": res.session.access_token,
        "refresh_token": res.session.refresh_token,
        "user_id": res.user.id
    }

@router.post("/login")
async def login(data:LoginSchema):
    try:
        res = supabase.auth.sign_in_with_password({
            "email":data.email,
            "password":data.password
        })
        if not res.session:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return {
            "access_token": res.session.access_token,
            "refresh_token": res.session.refresh_token,
            "expires_in": res.session.expires_in,
            "user_id": res.user.id
        }
    except AuthApiError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail=str(e))
@router.post('/confirm')
def confirm_email(payload: ConfirmRequest):
    try:
        return {
            "success": True,
            "message": "Email confirmed successfully"
        }

    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired confirmation token"
        )

@router.post("/refresh")
async def refresh_token(payload:RefreshTokenRequest):
    try:
        session = supabase.auth.refresh_session(payload.refresh_token)
        return {
            "access_token": session.session.access_token,
            "refresh_token": session.session.refresh_token,
            "expires_in": session.session.expires_in,
            "user_id": session.user.id
        }
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired refresh token"
        )


@router.post("/logout")
async def logout(authorization:str=Header(...),user=Depends(get_current_user)):
    token = authorization.replace("Bearer ", "")
    supabase.auth.sign_out(token)
    return {"success": True}
