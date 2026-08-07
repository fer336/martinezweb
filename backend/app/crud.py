import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Trabajo, TrabajoImagen
from app.schemas import TrabajoWrite
from app.storage import delete_images_by_urls

logger = logging.getLogger("martinez.crud")


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

    # Capturar las URLs que tenía antes de limpiar — para borrarlas de MinIO
    # las que ya no estén en la nueva lista (imágenes removidas por el usuario).
    old_urls = {img.url for img in trabajo.imagenes}
    new_urls = {img.url for img in data.imagenes}
    removed_urls = old_urls - new_urls

    trabajo.imagenes.clear()
    for i, img in enumerate(data.imagenes):
        trabajo.imagenes.append(TrabajoImagen(url=img.url, etiqueta=img.etiqueta, orden=i))

    await db.commit()
    await db.refresh(trabajo, attribute_names=["categoria", "zona", "imagenes"])

    # Best-effort: borrar de MinIO las imágenes que se quitaron en esta edición.
    if removed_urls:
        deleted = delete_images_by_urls(list(removed_urls))
        logger.info("Editado trabajo %d: %d imagen(es) borrada(s) de MinIO", trabajo.id, deleted)

    return trabajo


async def delete_trabajo_with_images(db: AsyncSession, trabajo: Trabajo) -> None:
    """Delete a trabajo and all its images from MinIO (best-effort)."""
    urls = [img.url for img in trabajo.imagenes]
    await db.delete(trabajo)
    await db.commit()
    if urls:
        deleted = delete_images_by_urls(urls)
        logger.info("Borrado trabajo %d: %d imagen(es) borrada(s) de MinIO", trabajo.id, deleted)
