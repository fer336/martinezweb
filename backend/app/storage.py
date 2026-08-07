import logging
import uuid

import boto3
from botocore.config import Config as BotoConfig

from app.config import settings
from app.imaging import compress_if_needed

logger = logging.getLogger("martinez.storage")

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_UPLOAD_BYTES = 8 * 1024 * 1024

_CONTENT_TYPE_EXT = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}

_ALLOWED_PREFIXES = {"trabajos", "hero"}


def _client():
    return boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint_url,
        aws_access_key_id=settings.s3_access_key_id,
        aws_secret_access_key=settings.s3_secret_access_key,
        region_name=settings.s3_region,
        config=BotoConfig(
            s3={"addressing_style": "path"},
            connect_timeout=8,
            read_timeout=15,
            retries={"max_attempts": 2},
        ),
    )


def upload_image(content: bytes, content_type: str, filename: str, prefix: str = "trabajos") -> str:
    content, content_type = compress_if_needed(content, content_type)
    ext = _CONTENT_TYPE_EXT.get(content_type, filename.rsplit(".", 1)[-1].lower() if "." in filename else "jpg")
    key = f"{prefix}/{uuid.uuid4().hex}.{ext}"
    _client().put_object(
        Bucket=settings.s3_bucket,
        Key=key,
        Body=content,
        ContentType=content_type,
    )
    return f"{settings.s3_public_base_url.rstrip('/')}/{key}"


def delete_image_by_url(url: str) -> bool:
    """Delete a single object from MinIO given its public URL.

    Returns True if the object was deleted, False if the URL does not
    belong to our bucket (safety: never delete arbitrary objects).

    Never raises — best-effort cleanup. Logs warnings on failure.
    """
    key = _url_to_key(url)
    if key is None:
        logger.warning("No se pudo borrar imagen: URL no pertenece al bucket: %s", url)
        return False
    try:
        _client().delete_object(Bucket=settings.s3_bucket, Key=key)
        return True
    except Exception:
        logger.warning("Error borrando objeto %s de MinIO", key, exc_info=True)
        return False


def delete_images_by_urls(urls: list[str]) -> int:
    """Delete multiple objects from MinIO. Returns count actually deleted."""
    from botocore.exceptions import BotoCoreError

    keys: list[str] = []
    for url in urls:
        key = _url_to_key(url)
        if key is not None:
            keys.append(key)

    if not keys:
        return 0

    try:
        client = _client()
        for key in keys:
            try:
                client.delete_object(Bucket=settings.s3_bucket, Key=key)
            except Exception:
                logger.warning("Error borrando objeto %s de MinIO", key, exc_info=True)
        return len(keys)
    except BotoCoreError:
        logger.warning("No se pudo conectar a MinIO para borrar %d objetos", len(keys), exc_info=True)
        return 0


def _url_to_key(url: str) -> str | None:
    """Extract the S3 object key from a public URL, with safety checks.

    Only returns a key if the URL starts with our configured public base URL
    and the key starts with an allowed prefix (trabajos/ or hero/).
    This prevents deleting arbitrary objects pointed at by crafted URLs.
    """
    base = settings.s3_public_base_url.rstrip("/")
    if not url or not url.startswith(base + "/"):
        return None
    key = url[len(base) + 1:]
    # Safety: only allow our known prefixes
    if not any(key.startswith(prefix + "/") for prefix in _ALLOWED_PREFIXES):
        return None
    return key
