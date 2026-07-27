from collections import defaultdict
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, Request, status

from app.config import settings
from app.rate_limit import limiter
from app.schemas import LoginIn, TokenOut
from app.security import create_access_token, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])

# Lockout por usuario además del rate limit por IP: sin esto alcanzaría con
# rotar de IP para seguir probando contraseñas contra la misma cuenta. En
# memoria de proceso porque el backend corre con un solo réplica (ver
# docker-compose.yml, deploy.replicas=1) — si algún día se escala a más de
# un réplica, esto necesita moverse a un store compartido (Redis).
_FAILED_LOGIN_WINDOW = timedelta(minutes=15)
_FAILED_LOGIN_MAX_ATTEMPTS = 5
_failed_logins: dict[str, list[datetime]] = defaultdict(list)


def _recent_failures(username: str) -> list[datetime]:
    now = datetime.now(timezone.utc)
    recent = [t for t in _failed_logins[username] if now - t < _FAILED_LOGIN_WINDOW]
    _failed_logins[username] = recent
    return recent


@router.post("/login", response_model=TokenOut)
@limiter.limit("10/minute")
def login(request: Request, data: LoginIn) -> TokenOut:
    if len(_recent_failures(data.username)) >= _FAILED_LOGIN_MAX_ATTEMPTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Demasiados intentos fallidos. Probá de nuevo en unos minutos.",
        )
    if data.username != settings.admin_username or not verify_password(
        data.password, settings.admin_password_hash
    ):
        _failed_logins[data.username].append(datetime.now(timezone.utc))
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario o contraseña incorrectos")
    _failed_logins.pop(data.username, None)
    return TokenOut(access_token=create_access_token(data.username))
