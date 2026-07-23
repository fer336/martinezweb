from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Trabajo, TrabajoImagen
from app.schemas import TrabajoWrite


async def create_trabajo(db: AsyncSession, data: TrabajoWrite) -> Trabajo:
    trabajo = Trabajo(
        categoria_id=data.categoria_id,
        titulo=data.titulo,
        zona_id=data.zona_id,
        orden=data.orden,
        publicado=data.publicado,
    )
    trabajo.imagenes = [
        TrabajoImagen(url=img.url, etiqueta=img.etiqueta, orden=i) for i, img in enumerate(data.imagenes)
    ]
    db.add(trabajo)
    await db.commit()
    await db.refresh(trabajo, attribute_names=["categoria", "zona", "imagenes"])
    return trabajo


async def update_trabajo(db: AsyncSession, trabajo: Trabajo, data: TrabajoWrite) -> Trabajo:
    trabajo.categoria_id = data.categoria_id
    trabajo.titulo = data.titulo
    trabajo.zona_id = data.zona_id
    trabajo.orden = data.orden
    trabajo.publicado = data.publicado

    trabajo.imagenes.clear()
    for i, img in enumerate(data.imagenes):
        trabajo.imagenes.append(TrabajoImagen(url=img.url, etiqueta=img.etiqueta, orden=i))

    await db.commit()
    await db.refresh(trabajo, attribute_names=["categoria", "zona", "imagenes"])
    return trabajo
