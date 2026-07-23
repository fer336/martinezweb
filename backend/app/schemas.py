from pydantic import BaseModel, ConfigDict, model_validator

from app.models import EtiquetaImagen, Trabajo


class CategoriaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nombre: str


class CategoriaCreate(BaseModel):
    nombre: str


class ZonaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nombre: str


class TrabajoImagenIn(BaseModel):
    url: str
    etiqueta: EtiquetaImagen | None = None


class TrabajoImagenOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    url: str
    etiqueta: EtiquetaImagen | None


class TrabajoWrite(BaseModel):
    categoria_id: int
    titulo: str
    zona_id: int | None = None
    orden: int = 0
    publicado: bool = True
    imagenes: list[TrabajoImagenIn]

    @model_validator(mode="after")
    def check_al_menos_una_imagen(self) -> "TrabajoWrite":
        if not self.imagenes:
            raise ValueError("El trabajo necesita al menos una imagen")
        return self


class TrabajoOut(BaseModel):
    id: int
    categoria_id: int
    categoria: str
    titulo: str
    zona_id: int | None
    zona: str | None
    orden: int
    publicado: bool
    imagenes: list[TrabajoImagenOut]

    @classmethod
    def from_model(cls, trabajo: Trabajo) -> "TrabajoOut":
        return cls(
            id=trabajo.id,
            categoria_id=trabajo.categoria_id,
            categoria=trabajo.categoria.nombre,
            titulo=trabajo.titulo,
            zona_id=trabajo.zona_id,
            zona=trabajo.zona.nombre if trabajo.zona else None,
            orden=trabajo.orden,
            publicado=trabajo.publicado,
            imagenes=[TrabajoImagenOut.model_validate(img) for img in trabajo.imagenes],
        )


class UploadOut(BaseModel):
    url: str


class SitioConfigOut(BaseModel):
    hero_image_url: str | None


class SitioConfigUpdate(BaseModel):
    hero_image_url: str


class LoginIn(BaseModel):
    username: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
