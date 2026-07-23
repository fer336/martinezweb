import uuid

import boto3
from botocore.config import Config as BotoConfig

from app.config import settings
from app.imaging import compress_if_needed

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_UPLOAD_BYTES = 8 * 1024 * 1024

_CONTENT_TYPE_EXT = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}


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
