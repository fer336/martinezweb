from fastapi import APIRouter, Depends, HTTPException

from app.github import trigger_deploy
from app.schemas import PublishOut
from app.security import require_admin

router = APIRouter(prefix="/admin/publish", tags=["admin-publish"], dependencies=[Depends(require_admin)])


@router.post("", response_model=PublishOut)
async def publish() -> PublishOut:
    try:
        await trigger_deploy()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"No se pudo disparar el deploy: {exc}") from exc
    return PublishOut(status="disparado")
