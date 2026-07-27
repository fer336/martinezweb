import logging

from fastapi import APIRouter, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from limits import parse
from limits.storage import MemoryStorage
from limits.strategies import FixedWindowRateLimiter
from slowapi.errors import RateLimitExceeded
from slowapi.extension import _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from sqlalchemy.exc import DBAPIError
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from app.config import settings
from app.rate_limit import limiter
from app.routers import auth, catalog, config as config_router, trabajos, uploads

logger = logging.getLogger("martinez.api")

app = FastAPI(
    title="Martínez Gas-Plomería · CMS API",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

app.state.limiter = limiter


def _rate_limit_handler(request: Request, exc: RateLimitExceeded) -> Response:
    logger.warning("Rate limit excedido desde %s: %s %s", get_remote_address(request), request.method, request.url.path)
    return _rate_limit_exceeded_handler(request, exc)


app.add_exception_handler(RateLimitExceeded, _rate_limit_handler)


@app.exception_handler(DBAPIError)
async def db_error_handler(request: Request, exc: DBAPIError) -> JSONResponse:
    # exc_info=exc deja el detalle completo (incluido el SQL) en el log del
    # servidor para debug, pero al cliente solo le devolvemos un mensaje
    # genérico: nunca SQL ni datos internos.
    logger.error("Error de base de datos en %s %s", request.method, request.url.path, exc_info=exc)
    return JSONResponse(
        status_code=503,
        content={"detail": "Servicio no disponible en este momento, intentá de nuevo en unos segundos"},
    )


# Límite general (60/min por IP) para toda la API. No usamos SlowAPIMiddleware
# acá a propósito: en la versión de FastAPI instalada, app.routes envuelve las
# rutas incluidas vía include_router() en un objeto interno que
# slowapi.middleware._find_route_handler no sabe recorrer, así que ese
# middleware nunca encuentra el handler y termina sin aplicar ningún límite
# (verificado: 65 requests seguidos a /api/health devolvían 200). El
# decorator @limiter.limit(...) en rutas puntuales (ver auth.py) no depende
# de esa resolución y sí funciona, así que lo seguimos usando para /auth/login.
_general_limit = parse("60/minute")
_general_storage = MemoryStorage()
_general_limiter = FixedWindowRateLimiter(_general_storage)


class GeneralRateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        client_ip = get_remote_address(request)
        if not _general_limiter.hit(_general_limit, client_ip):
            logger.warning("Rate limit general excedido desde %s: %s %s", client_ip, request.method, request.url.path)
            return JSONResponse(
                status_code=429,
                content={"detail": "Demasiadas solicitudes, probá de nuevo en un momento"},
            )
        return await call_next(request)


class Log404Middleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        if response.status_code == 404:
            logger.warning("404 desde %s: %s %s", get_remote_address(request), request.method, request.url.path)
        return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GeneralRateLimitMiddleware)
app.add_middleware(Log404Middleware)

# Todo el backend cuelga de /api: así en Traefik alcanza con una sola regla
# de PathPrefix("/api") para diferenciarlo del frontend, sin tener que
# agregar un router nuevo cada vez que se suma un endpoint.
api = APIRouter(prefix="/api")
api.include_router(auth.router)
api.include_router(trabajos.public_router)
api.include_router(trabajos.admin_router)
api.include_router(catalog.router)
api.include_router(config_router.public_router)
api.include_router(config_router.admin_router)
api.include_router(uploads.router)


@api.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(api)
