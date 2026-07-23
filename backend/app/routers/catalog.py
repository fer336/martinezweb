from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import Categoria, Zona
from app.schemas import CategoriaCreate, CategoriaOut, ZonaOut
from app.security import require_admin

router = APIRouter(prefix="/admin", tags=["admin-catalog"], dependencies=[Depends(require_admin)])


@router.get("/categorias", response_model=list[CategoriaOut])
async def list_categorias(db: AsyncSession = Depends(get_db)) -> list[Categoria]:
    return list((await db.scalars(select(Categoria).order_by(Categoria.nombre))).all())


@router.post("/categorias", response_model=CategoriaOut, status_code=201)
async def create_categoria(data: CategoriaCreate, db: AsyncSession = Depends(get_db)) -> Categoria:
    nombre = data.nombre.strip()
    if not nombre:
        raise HTTPException(status_code=422, detail="El nombre no puede estar vacío")
    categoria = Categoria(nombre=nombre)
    db.add(categoria)
    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Ya existe una categoría con ese nombre") from exc
    await db.refresh(categoria)
    return categoria


@router.get("/zonas", response_model=list[ZonaOut])
async def list_zonas(db: AsyncSession = Depends(get_db)) -> list[Zona]:
    return list((await db.scalars(select(Zona).order_by(Zona.nombre))).all())
