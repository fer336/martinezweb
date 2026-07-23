from sqlalchemy.ext.asyncio import AsyncSession

from app.models import RolImagen, Trabajo, TrabajoImagen
from app.schemas import TrabajoWrite


def _imagenes_from_payload(data: TrabajoWrite) -> dict[RolImagen, str]:
    imagenes: dict[RolImagen, str] = {}
    if data.antes_url:
        imagenes[RolImagen.antes] = data.antes_url
    if data.despues_url:
        imagenes[RolImagen.despues] = data.despues_url
    if data.foto_url:
        imagenes[RolImagen.foto] = data.foto_url
    return imagenes


async def create_trabajo(db: AsyncSession, data: TrabajoWrite) -> Trabajo:
    trabajo = Trabajo(
        categoria_id=data.categoria_id,
        titulo=data.titulo,
        zona_id=data.zona_id,
        tipo=data.tipo,
        orden=data.orden,
        publicado=data.publicado,
    )
    for rol, url in _imagenes_from_payload(data).items():
        trabajo.imagenes.append(TrabajoImagen(rol=rol, url=url))
    db.add(trabajo)
    await db.commit()
    await db.refresh(trabajo, attribute_names=["categoria", "zona", "imagenes"])
    return trabajo


async def update_trabajo(db: AsyncSession, trabajo: Trabajo, data: TrabajoWrite) -> Trabajo:
    trabajo.categoria_id = data.categoria_id
    trabajo.titulo = data.titulo
    trabajo.zona_id = data.zona_id
    trabajo.tipo = data.tipo
    trabajo.orden = data.orden
    trabajo.publicado = data.publicado

    nuevas = _imagenes_from_payload(data)
    existentes = {img.rol: img for img in trabajo.imagenes}

    for rol, url in nuevas.items():
        if rol in existentes:
            existentes[rol].url = url
        else:
            trabajo.imagenes.append(TrabajoImagen(rol=rol, url=url))
    for rol, img in list(existentes.items()):
        if rol not in nuevas:
            trabajo.imagenes.remove(img)

    await db.commit()
    await db.refresh(trabajo, attribute_names=["categoria", "zona", "imagenes"])
    return trabajo
