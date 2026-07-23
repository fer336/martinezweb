from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool

from app.schemas import UploadOut
from app.security import require_admin
from app.storage import ALLOWED_CONTENT_TYPES, MAX_UPLOAD_BYTES, upload_image

router = APIRouter(prefix="/admin/uploads", tags=["admin-uploads"], dependencies=[Depends(require_admin)])

_ALLOWED_PREFIXES = {"trabajos", "hero"}


@router.post("", response_model=UploadOut)
async def upload(file: UploadFile, prefix: str = Form("trabajos")) -> UploadOut:
    if prefix not in _ALLOWED_PREFIXES:
        raise HTTPException(status_code=400, detail="prefix inválido")
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Formato de imagen no soportado (usá jpg, png o webp)")
    content = await file.read()
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=400, detail="La imagen supera el tamaño máximo permitido (8MB)")
    try:
        url = await run_in_threadpool(upload_image, content, file.content_type, file.filename or "foto.jpg", prefix)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"No se pudo subir la imagen: {exc}") from exc
    return UploadOut(url=url)
