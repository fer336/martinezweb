import logging

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import SitioConfig
from app.schemas import SitioConfigOut, SitioConfigUpdate
from app.security import require_admin
from app.storage import delete_image_by_url

logger = logging.getLogger("martinez.config")

public_router = APIRouter(tags=["config"])
admin_router = APIRouter(prefix="/admin/config", tags=["admin-config"], dependencies=[Depends(require_admin)])


async def _get_or_create(db: AsyncSession) -> SitioConfig:
    config = await db.get(SitioConfig, 1)
    if config is None:
        config = SitioConfig(id=1)
        db.add(config)
        await db.commit()
        await db.refresh(config)
    return config


@public_router.get("/config", response_model=SitioConfigOut)
async def get_config(db: AsyncSession = Depends(get_db)) -> SitioConfig:
    return await _get_or_create(db)


@admin_router.get("", response_model=SitioConfigOut)
async def get_admin_config(db: AsyncSession = Depends(get_db)) -> SitioConfig:
    return await _get_or_create(db)


@admin_router.put("", response_model=SitioConfigOut)
async def update_config(data: SitioConfigUpdate, db: AsyncSession = Depends(get_db)) -> SitioConfig:
    config = await _get_or_create(db)
    old_url = config.hero_image_url
    config.hero_image_url = data.hero_image_url
    await db.commit()
    await db.refresh(config)

    # Best-effort: borrar la imagen anterior del Hero de MinIO si cambió.
    if old_url and old_url != data.hero_image_url:
        if delete_image_by_url(old_url):
            logger.info("Imagen del Hero actualizada: imagen vieja borrada de MinIO (%s)", old_url)

    return config
