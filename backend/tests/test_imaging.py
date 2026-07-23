from io import BytesIO

from PIL import Image

from app.imaging import MAX_BYTES, compress_if_needed


def _make_jpeg(size: tuple[int, int], quality: int = 95) -> bytes:
    image = Image.new("RGB", size, color=(120, 45, 200))
    # ruido para que no comprima a casi nada y realmente supere 1MB
    pixels = image.load()
    for x in range(0, size[0], 3):
        for y in range(0, size[1], 3):
            pixels[x, y] = (x % 256, y % 256, (x + y) % 256)
    buffer = BytesIO()
    image.save(buffer, format="JPEG", quality=quality)
    return buffer.getvalue()


def test_small_image_is_not_recompressed():
    small = _make_jpeg((200, 200))
    assert len(small) <= MAX_BYTES
    data, content_type = compress_if_needed(small, "image/jpeg")
    assert data == small
    assert content_type == "image/jpeg"


def test_large_image_is_compressed_under_limit():
    large = _make_jpeg((4000, 3000), quality=100)
    assert len(large) > MAX_BYTES
    data, content_type = compress_if_needed(large, "image/jpeg")
    assert len(data) <= MAX_BYTES
    assert content_type == "image/jpeg"
    # sigue siendo una imagen válida
    Image.open(BytesIO(data)).verify()
