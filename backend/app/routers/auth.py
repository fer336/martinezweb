from fastapi import APIRouter, HTTPException, status

from app.config import settings
from app.schemas import LoginIn, TokenOut
from app.security import create_access_token, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenOut)
def login(data: LoginIn) -> TokenOut:
    if data.username != settings.admin_username or not verify_password(
        data.password, settings.admin_password_hash
    ):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario o contraseña incorrectos")
    return TokenOut(access_token=create_access_token(data.username))
