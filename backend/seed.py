"""Carga categorías, zonas y los trabajos placeholder actuales como datos iniciales.

Uso: python seed.py
"""

import asyncio

from sqlalchemy import select

from app.db import SessionLocal
from app.models import Categoria, EtiquetaImagen, Trabajo, TrabajoImagen, Zona

SITE_BASE = "https://fer336.github.io/martinezweb"

CATEGORIAS = ["Reparación de bombas", "Plomería y gas"]
ZONAS = ["Pinamar", "Valeria del Mar", "Ostende", "Cariló", "Costa Esmeralda"]

SEED = [
    {
        "categoria": "Reparación de bombas",
        "titulo": "Cambio de motor en bomba Rowa",
        "zona": "Cariló",
        "imagenes": [
            (f"{SITE_BASE}/assets/trabajos/placeholder-antes.svg", EtiquetaImagen.antes),
            (f"{SITE_BASE}/assets/trabajos/placeholder-despues.svg", EtiquetaImagen.despues),
        ],
    },
    {
        "categoria": "Plomería y gas",
        "titulo": "Reparación de cañerías e instalación de artefactos",
        "zona": "Valeria del Mar",
        "imagenes": [(f"{SITE_BASE}/assets/trabajos/placeholder-trabajo.svg", None)],
    },
    {
        "categoria": "Plomería y gas",
        "titulo": "Instalación de gas para vivienda",
        "zona": "Ostende",
        "imagenes": [(f"{SITE_BASE}/assets/trabajos/placeholder-trabajo.svg", None)],
    },
]


async def _get_or_create(db, model, nombre: str):
    existing = (await db.scalars(select(model).where(model.nombre == nombre))).first()
    if existing:
        return existing
    obj = model(nombre=nombre)
    db.add(obj)
    await db.flush()
    return obj


async def main() -> None:
    async with SessionLocal() as db:
        categorias = {nombre: await _get_or_create(db, Categoria, nombre) for nombre in CATEGORIAS}
        zonas = {nombre: await _get_or_create(db, Zona, nombre) for nombre in ZONAS}
        await db.commit()

        existentes = (await db.scalars(select(Trabajo))).first()
        if existentes:
            print("Ya hay trabajos cargados, no se hace seed de trabajos (categorías/zonas sí se sincronizaron).")
            return

        for orden, data in enumerate(SEED):
            trabajo = Trabajo(
                categoria_id=categorias[data["categoria"]].id,
                titulo=data["titulo"],
                zona_id=zonas[data["zona"]].id if data["zona"] else None,
                orden=orden,
                publicado=True,
            )
            for i, (url, etiqueta) in enumerate(data["imagenes"]):
                trabajo.imagenes.append(TrabajoImagen(url=url, etiqueta=etiqueta, orden=i))
            db.add(trabajo)
        await db.commit()
        print(f"Cargados {len(CATEGORIAS)} categorías, {len(ZONAS)} zonas y {len(SEED)} trabajos de ejemplo.")


if __name__ == "__main__":
    asyncio.run(main())
