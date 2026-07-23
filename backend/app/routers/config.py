from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import SitioConfig
from app.schemas import SitioConfigOut, SitioConfigUpdate
from app.security import require_admin

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
    config.hero_image_url = data.hero_image_url
    await db.commit()
    await db.refresh(config)
    return config
