import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class EtiquetaImagen(str, enum.Enum):
    antes = "antes"
    despues = "despues"


class Categoria(Base):
    __tablename__ = "categorias"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(80), unique=True)

    trabajos: Mapped[list["Trabajo"]] = relationship(back_populates="categoria")


class Zona(Base):
    __tablename__ = "zonas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(80), unique=True)

    trabajos: Mapped[list["Trabajo"]] = relationship(back_populates="zona")


class Trabajo(Base):
    __tablename__ = "trabajos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    categoria_id: Mapped[int] = mapped_column(ForeignKey("categorias.id"))
    titulo: Mapped[str] = mapped_column(String(200))
    zona_id: Mapped[int | None] = mapped_column(ForeignKey("zonas.id"), nullable=True)
    orden: Mapped[int] = mapped_column(Integer, default=0)
    publicado: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    categoria: Mapped[Categoria] = relationship(back_populates="trabajos", lazy="selectin")
    zona: Mapped[Zona | None] = relationship(back_populates="trabajos", lazy="selectin")
    imagenes: Mapped[list["TrabajoImagen"]] = relationship(
        back_populates="trabajo",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="TrabajoImagen.orden",
    )


class SitioConfig(Base):
    """Configuración global del sitio (fila única, id siempre 1)."""

    __tablename__ = "sitio_config"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    hero_image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class TrabajoImagen(Base):
    __tablename__ = "trabajo_imagenes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    trabajo_id: Mapped[int] = mapped_column(ForeignKey("trabajos.id", ondelete="CASCADE"))
    url: Mapped[str] = mapped_column(String(500))
    orden: Mapped[int] = mapped_column(Integer, default=0)
    etiqueta: Mapped[EtiquetaImagen | None] = mapped_column(Enum(EtiquetaImagen, name="etiquetaimagen"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    trabajo: Mapped[Trabajo] = relationship(back_populates="imagenes")
