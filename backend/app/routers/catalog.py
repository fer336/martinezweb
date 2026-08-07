import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import Categoria, Trabajo, Zona
from app.schemas import CategoriaCreate, CategoriaOut, ZonaOut
from app.security import require_admin
from app.storage import delete_images_by_urls

logger = logging.getLogger("martinez.catalog")

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


@router.delete("/categorias/{categoria_id}", status_code=204)
async def delete_categoria(categoria_id: int, db: AsyncSession = Depends(get_db)) -> None:
    """Borrar una categoría y todos sus trabajos + imágenes en MinIO (cascade).

    Borra explícitamente cada trabajo (lo que dispara el cascade ORM para
    trabajo_imagenes) y luego la categoría. Las imágenes en MinIO se borran
    best-effort.
    """
    categoria = await db.get(Categoria, categoria_id)
    if categoria is None:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    # Cargar los trabajos para obtener URLs de imágenes antes de borrar.
    stmt = select(Trabajo).where(Trabajo.categoria_id == categoria_id)
    trabajos = list((await db.scalars(stmt)).all())

    # Recolectar todas las URLs de imágenes para borrar de MinIO después.
    image_urls: list[str] = []
    for trabajo in trabajos:
        for img in trabajo.imagenes:
            image_urls.append(img.url)

    # Borrar los trabajos primero (evita la violación de FK en SQLite/Postgres
    # que ocurriría si intentáramos borrar la categoría directamente).
    for trabajo in trabajos:
        await db.delete(trabajo)

    await db.delete(categoria)
    await db.commit()

    # Best-effort: borrar todas las imágenes de MinIO.
    if image_urls:
        deleted = delete_images_by_urls(image_urls)
        logger.info(
            "Borrada categoría %d ('%s'): %d trabajos, %d imagen(es) borrada(s) de MinIO",
            categoria_id,
            categoria.nombre,
            len(trabajos),
            deleted,
        )


@router.get("/zonas", response_model=list[ZonaOut])
async def list_zonas(db: AsyncSession = Depends(get_db)) -> list[Zona]:
    return list((await db.scalars(select(Zona).order_by(Zona.nombre))).all())
