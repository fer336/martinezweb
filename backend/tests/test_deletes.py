"""Tests for delete endpoints: categoria cascade, upload by URL, and storage safety checks."""
from unittest.mock import patch

from app.storage import _url_to_key


# --- _url_to_key safety checks ---

def test_url_to_key_extracts_key_from_valid_url():
    with patch("app.storage.settings") as mock_settings:
        mock_settings.s3_public_base_url = "https://s3.qeva.xyz/martinez-fotos"
        key = _url_to_key("https://s3.qeva.xyz/martinez-fotos/trabajos/abc123.jpg")
        assert key == "trabajos/abc123.jpg"


def test_url_to_key_rejects_foreign_url():
    with patch("app.storage.settings") as mock_settings:
        mock_settings.s3_public_base_url = "https://s3.qeva.xyz/martinez-fotos"
        assert _url_to_key("https://evil.com/trabajos/abc.jpg") is None
        assert _url_to_key("https://s3.qeva.xyz/other-bucket/trabajos/abc.jpg") is None


def test_url_to_key_rejects_disallowed_prefix():
    with patch("app.storage.settings") as mock_settings:
        mock_settings.s3_public_base_url = "https://s3.qeva.xyz/martinez-fotos"
        assert _url_to_key("https://s3.qeva.xyz/martinez-fotos/../../etc/passwd") is None
        assert _url_to_key("https://s3.qeva.xyz/martinez-fotos/arbitrary/file.jpg") is None


def test_url_to_key_allows_hero_prefix():
    with patch("app.storage.settings") as mock_settings:
        mock_settings.s3_public_base_url = "https://s3.qeva.xyz/martinez-fotos"
        key = _url_to_key("https://s3.qeva.xyz/martinez-fotos/hero/xyz.png")
        assert key == "hero/xyz.png"


# --- DELETE /admin/uploads ---

import json


def _delete_uploads(client, url, headers=None):
    """Helper: TestClient.delete doesn't accept json=, so use request()."""
    return client.request(
        "DELETE",
        "/api/admin/uploads",
        content=json.dumps({"url": url}),
        headers={**(headers or {}), "Content-Type": "application/json"},
    )


def test_delete_upload_requires_auth(client):
    response = _delete_uploads(client, "https://x/y.jpg")
    assert response.status_code == 401


def test_delete_upload_foreign_url_returns_404(client, auth_headers):
    """URLs that don't belong to our bucket must be rejected (safety)."""
    with patch("app.storage.settings") as mock_settings:
        mock_settings.s3_public_base_url = "https://s3.qeva.xyz/martinez-fotos"
        response = _delete_uploads(client, "https://evil.com/trabajos/abc.jpg", auth_headers)
        assert response.status_code == 404


def test_delete_upload_valid_url_calls_minio(client, auth_headers):
    """A valid URL from our bucket should attempt deletion (mocked)."""
    url = "https://s3.qeva.xyz/martinez-fotos/trabajos/abc123.jpg"

    with patch("app.storage.settings") as mock_settings, \
         patch("app.storage._client") as mock_client_factory:
        mock_settings.s3_public_base_url = "https://s3.qeva.xyz/martinez-fotos"
        mock_client = mock_client_factory.return_value

        response = _delete_uploads(client, url, auth_headers)

        assert response.status_code == 204
        mock_client.delete_object.assert_called_once_with(
            Bucket=mock_settings.s3_bucket,
            Key="trabajos/abc123.jpg",
        )


# --- DELETE /admin/categorias/{id} cascade ---

def _payload(catalogo, **overrides):
    payload = {
        "categoria_id": catalogo["categoria_id"],
        "titulo": "Instalación de prueba",
        "zona_id": catalogo["zona_id"],
        "imagenes": [{"url": "https://s3.qeva.xyz/martinez-fotos/trabajos/foto.jpg", "etiqueta": None}],
        "orden": 0,
        "publicado": True,
    }
    payload.update(overrides)
    return payload


def test_delete_categoria_cascade_deletes_trabajos(client, auth_headers, catalogo):
    """Deleting a category must also delete all its trabajos."""
    with patch("app.storage.settings") as mock_settings, \
         patch("app.storage._client") as mock_client_factory:
        mock_settings.s3_public_base_url = "https://s3.qeva.xyz/martinez-fotos"
        mock_settings.s3_bucket = "martinez-fotos"
        mock_client_factory.return_value  # no-op mock

        # Crear dos trabajos en la categoría
        client.post("/api/admin/trabajos", json=_payload(catalogo, titulo="Trabajo 1"), headers=auth_headers)
        client.post("/api/admin/trabajos", json=_payload(catalogo, titulo="Trabajo 2"), headers=auth_headers)

        # Verificar que existen
        assert len(client.get("/api/trabajos").json()) == 2

        # Borrar la categoría
        response = client.delete(f"/api/admin/categorias/{catalogo['categoria_id']}", headers=auth_headers)
        assert response.status_code == 204

    # Los trabajos deben haberse borrado en cascada
    assert client.get("/api/trabajos").json() == []

    # La categoría ya no existe
    categorias = client.get("/api/admin/categorias", headers=auth_headers).json()
    assert not any(c["id"] == catalogo["categoria_id"] for c in categorias)


def test_delete_categoria_borra_imagenes_de_minio(client, auth_headers, catalogo):
    """Deleting a category must also delete its images from MinIO (best-effort)."""
    url1 = "https://s3.qeva.xyz/martinez-fotos/trabajos/aaa.jpg"
    url2 = "https://s3.qeva.xyz/martinez-fotos/trabajos/bbb.jpg"

    with patch("app.storage.settings") as mock_settings, \
         patch("app.storage._client") as mock_client_factory:
        mock_settings.s3_public_base_url = "https://s3.qeva.xyz/martinez-fotos"
        mock_settings.s3_bucket = "martinez-fotos"
        mock_client = mock_client_factory.return_value

        client.post(
            "/api/admin/trabajos",
            json=_payload(catalogo, titulo="T1", imagenes=[{"url": url1, "etiqueta": None}]),
            headers=auth_headers,
        )
        client.post(
            "/api/admin/trabajos",
            json=_payload(catalogo, titulo="T2", imagenes=[{"url": url2, "etiqueta": None}]),
            headers=auth_headers,
        )

        response = client.delete(f"/api/admin/categorias/{catalogo['categoria_id']}", headers=auth_headers)
        assert response.status_code == 204

        # Debe haber llamado delete_object para ambas imágenes
        deleted_keys = {call.kwargs["Key"] for call in mock_client.delete_object.call_args_list}
        assert "trabajos/aaa.jpg" in deleted_keys
        assert "trabajos/bbb.jpg" in deleted_keys


def test_delete_categoria_missing_returns_404(client, auth_headers):
    response = client.delete("/api/admin/categorias/999", headers=auth_headers)
    assert response.status_code == 404


def test_delete_categoria_requires_auth(client):
    response = client.delete("/api/admin/categorias/1")
    assert response.status_code == 401


# --- DELETE /admin/trabajos/{id} borra imágenes de MinIO ---

def test_delete_trabajo_borra_imagenes_de_minio(client, auth_headers, catalogo):
    """Deleting a trabajo must also delete its images from MinIO."""
    url = "https://s3.qeva.xyz/martinez-fotos/trabajos/test123.jpg"

    with patch("app.storage.settings") as mock_settings, \
         patch("app.storage._client") as mock_client_factory:
        mock_settings.s3_public_base_url = "https://s3.qeva.xyz/martinez-fotos"
        mock_settings.s3_bucket = "martinez-fotos"
        mock_client = mock_client_factory.return_value

        created = client.post(
            "/api/admin/trabajos",
            json=_payload(catalogo, titulo="Test", imagenes=[{"url": url, "etiqueta": None}]),
            headers=auth_headers,
        ).json()

        response = client.delete(f"/api/admin/trabajos/{created['id']}", headers=auth_headers)
        assert response.status_code == 204

        mock_client.delete_object.assert_called_with(
            Bucket="martinez-fotos",
            Key="trabajos/test123.jpg",
        )


# --- UPDATE /admin/trabajos borra imágenes removidas ---

def test_update_trabajo_borra_imagenes_removidas_de_minio(client, auth_headers, catalogo):
    """Editing a trabajo and removing an image must delete it from MinIO."""
    old_url = "https://s3.qeva.xyz/martinez-fotos/trabajos/old.jpg"
    new_url = "https://s3.qeva.xyz/martinez-fotos/trabajos/new.jpg"

    with patch("app.storage.settings") as mock_settings, \
         patch("app.storage._client") as mock_client_factory:
        mock_settings.s3_public_base_url = "https://s3.qeva.xyz/martinez-fotos"
        mock_settings.s3_bucket = "martinez-fotos"
        mock_client = mock_client_factory.return_value

        created = client.post(
            "/api/admin/trabajos",
            json=_payload(catalogo, titulo="Test", imagenes=[
                {"url": old_url, "etiqueta": None},
                {"url": new_url, "etiqueta": None},
            ]),
            headers=auth_headers,
        ).json()

        # Editar: dejar solo la imagen nueva (quitar la vieja)
        client.put(
            f"/api/admin/trabajos/{created['id']}",
            json=_payload(catalogo, titulo="Test", imagenes=[{"url": new_url, "etiqueta": None}]),
            headers=auth_headers,
        )

        # Debe haber borrado la imagen vieja de MinIO
        deleted_keys = {call.kwargs["Key"] for call in mock_client.delete_object.call_args_list}
        assert "trabajos/old.jpg" in deleted_keys


# --- UPDATE /admin/config borra imagen vieja del Hero ---

def test_update_config_borra_hero_viejo_de_minio(client, auth_headers):
    """Changing the hero image must delete the old one from MinIO."""
    old_url = "https://s3.qeva.xyz/martinez-fotos/hero/old.jpg"
    new_url = "https://s3.qeva.xyz/martinez-fotos/hero/new.jpg"

    with patch("app.storage.settings") as mock_settings, \
         patch("app.storage._client") as mock_client_factory:
        mock_settings.s3_public_base_url = "https://s3.qeva.xyz/martinez-fotos"
        mock_settings.s3_bucket = "martinez-fotos"
        mock_client = mock_client_factory.return_value

        # Set initial hero
        client.put("/api/admin/config", json={"hero_image_url": old_url}, headers=auth_headers)

        # Change hero
        client.put("/api/admin/config", json={"hero_image_url": new_url}, headers=auth_headers)

        # Old image should have been deleted
        deleted_keys = {call.kwargs["Key"] for call in mock_client.delete_object.call_args_list}
        assert "hero/old.jpg" in deleted_keys
