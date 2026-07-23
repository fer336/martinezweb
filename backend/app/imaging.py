from io import BytesIO

from PIL import Image

MAX_BYTES = 1 * 1024 * 1024
_QUALITY_STEPS = (85, 75, 65, 55, 45, 35)
_MIN_DIMENSION = 500


def compress_if_needed(content: bytes, content_type: str) -> tuple[bytes, str]:
    """Si la imagen ya pesa <=1MB la deja tal cual. Si no, la recomprime como
    JPEG bajando calidad y, si hace falta, achicando la resolución hasta
    entrar en el límite."""
    if len(content) <= MAX_BYTES:
        return content, content_type

    image = Image.open(BytesIO(content))
    image = image.convert("RGB")

    for quality in _QUALITY_STEPS:
        buffer = BytesIO()
        image.save(buffer, format="JPEG", quality=quality, optimize=True)
        data = buffer.getvalue()
        if len(data) <= MAX_BYTES:
            return data, "image/jpeg"

    width, height = image.size
    data = buffer.getvalue()
    while len(data) > MAX_BYTES and max(width, height) > _MIN_DIMENSION:
        width = int(width * 0.85)
        height = int(height * 0.85)
        resized = image.resize((width, height), Image.LANCZOS)
        buffer = BytesIO()
        resized.save(buffer, format="JPEG", quality=70, optimize=True)
        data = buffer.getvalue()

    return data, "image/jpeg"
