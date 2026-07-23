from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import auth, catalog, config as config_router, trabajos, uploads

app = FastAPI(
    title="Martínez Gas-Plomería · CMS API",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
