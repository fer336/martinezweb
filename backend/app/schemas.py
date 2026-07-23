from pydantic import BaseModel, ConfigDict, model_validator

from app.models import RolImagen, Trabajo, TipoTrabajo


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


class TrabajoWrite(BaseModel):
    categoria_id: int
    titulo: str
    zona_id: int | None = None
    tipo: TipoTrabajo
    antes_url: str | None = None
    despues_url: str | None = None
    foto_url: str | None = None
    orden: int = 0
    publicado: bool = True

    @model_validator(mode="after")
    def check_urls_match_tipo(self) -> "TrabajoWrite":
        if self.tipo == TipoTrabajo.antes_despues:
            if not self.antes_url or not self.despues_url:
                raise ValueError("antes_url y despues_url son obligatorios para tipo antes_despues")
        elif self.tipo == TipoTrabajo.foto:
            if not self.foto_url:
                raise ValueError("foto_url es obligatorio para tipo foto")
        return self


class TrabajoOut(BaseModel):
    id: int
    categoria_id: int
    categoria: str
    titulo: str
    zona_id: int | None
    zona: str | None
    tipo: TipoTrabajo
    antes_url: str | None
    despues_url: str | None
    foto_url: str | None
    orden: int
    publicado: bool

    @classmethod
    def from_model(cls, trabajo: Trabajo) -> "TrabajoOut":
        por_rol = {img.rol: img.url for img in trabajo.imagenes}
        return cls(
            id=trabajo.id,
            categoria_id=trabajo.categoria_id,
            categoria=trabajo.categoria.nombre,
            titulo=trabajo.titulo,
            zona_id=trabajo.zona_id,
            zona=trabajo.zona.nombre if trabajo.zona else None,
            tipo=trabajo.tipo,
            antes_url=por_rol.get(RolImagen.antes),
            despues_url=por_rol.get(RolImagen.despues),
            foto_url=por_rol.get(RolImagen.foto),
            orden=trabajo.orden,
            publicado=trabajo.publicado,
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


class PublishOut(BaseModel):
    status: str
    workflow_run_url: str | None = None
