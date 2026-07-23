from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.db import get_db
from app.models import Trabajo
from app.schemas import TrabajoOut, TrabajoWrite
from app.security import require_admin

public_router = APIRouter(tags=["trabajos"])
admin_router = APIRouter(prefix="/admin/trabajos", tags=["admin-trabajos"], dependencies=[Depends(require_admin)])


@public_router.get("/trabajos", response_model=list[TrabajoOut])
async def list_public_trabajos(db: AsyncSession = Depends(get_db)) -> list[TrabajoOut]:
    stmt = select(Trabajo).where(Trabajo.publicado.is_(True)).order_by(Trabajo.orden, Trabajo.id)
    trabajos = (await db.scalars(stmt)).all()
    return [TrabajoOut.from_model(t) for t in trabajos]


@admin_router.get("", response_model=list[TrabajoOut])
async def list_all_trabajos(db: AsyncSession = Depends(get_db)) -> list[TrabajoOut]:
    stmt = select(Trabajo).order_by(Trabajo.orden, Trabajo.id)
    trabajos = (await db.scalars(stmt)).all()
    return [TrabajoOut.from_model(t) for t in trabajos]


async def _validate_refs(db: AsyncSession, data: TrabajoWrite) -> None:
    from app.models import Categoria, Zona

    if await db.get(Categoria, data.categoria_id) is None:
        raise HTTPException(status_code=422, detail="categoria_id inválido")
    if data.zona_id is not None and await db.get(Zona, data.zona_id) is None:
        raise HTTPException(status_code=422, detail="zona_id inválido")


@admin_router.post("", response_model=TrabajoOut, status_code=201)
async def create_trabajo(data: TrabajoWrite, db: AsyncSession = Depends(get_db)) -> TrabajoOut:
    await _validate_refs(db, data)
    trabajo = await crud.create_trabajo(db, data)
    return TrabajoOut.from_model(trabajo)


async def _get_or_404(db: AsyncSession, trabajo_id: int) -> Trabajo:
    trabajo = await db.get(Trabajo, trabajo_id)
    if trabajo is None:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado")
    return trabajo


@admin_router.put("/{trabajo_id}", response_model=TrabajoOut)
async def update_trabajo(trabajo_id: int, data: TrabajoWrite, db: AsyncSession = Depends(get_db)) -> TrabajoOut:
    await _validate_refs(db, data)
    trabajo = await _get_or_404(db, trabajo_id)
    trabajo = await crud.update_trabajo(db, trabajo, data)
    return TrabajoOut.from_model(trabajo)


@admin_router.delete("/{trabajo_id}", status_code=204)
async def delete_trabajo(trabajo_id: int, db: AsyncSession = Depends(get_db)) -> None:
    trabajo = await _get_or_404(db, trabajo_id)
    await db.delete(trabajo)
    await db.commit()
