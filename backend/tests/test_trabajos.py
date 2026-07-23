def _payload(catalogo, **overrides):
    payload = {
        "categoria_id": catalogo["categoria_id"],
        "titulo": "Instalación de prueba",
        "zona_id": catalogo["zona_id"],
        "tipo": "foto",
        "foto_url": "https://example.com/foto.jpg",
        "orden": 0,
        "publicado": True,
    }
    payload.update(overrides)
    return payload


def test_create_and_list_public(client, auth_headers, catalogo):
    response = client.post("/api/admin/trabajos", json=_payload(catalogo), headers=auth_headers)
    assert response.status_code == 201
    body = response.json()
    assert body["categoria"] == "Plomería y gas"
    assert body["zona"] == "Pinamar"

    public = client.get("/api/trabajos")
    assert public.status_code == 200
    assert len(public.json()) == 1
    assert public.json()[0]["titulo"] == "Instalación de prueba"


def test_unpublished_not_in_public_list(client, auth_headers, catalogo):
    client.post("/api/admin/trabajos", json=_payload(catalogo, publicado=False), headers=auth_headers)

    public = client.get("/api/trabajos")
    assert public.status_code == 200
    assert public.json() == []

    admin_list = client.get("/api/admin/trabajos", headers=auth_headers)
    assert len(admin_list.json()) == 1


def test_antes_despues_requires_both_urls(client, auth_headers, catalogo):
    payload = _payload(catalogo, tipo="antes_despues", foto_url=None, antes_url="https://example.com/antes.jpg")
    response = client.post("/api/admin/trabajos", json=payload, headers=auth_headers)
    assert response.status_code == 422


def test_invalid_categoria_id_rejected(client, auth_headers, catalogo):
    payload = _payload(catalogo, categoria_id=9999)
    response = client.post("/api/admin/trabajos", json=payload, headers=auth_headers)
    assert response.status_code == 422


def test_update_and_delete(client, auth_headers, catalogo):
    created = client.post("/api/admin/trabajos", json=_payload(catalogo), headers=auth_headers).json()
    trabajo_id = created["id"]

    update = client.put(
        f"/api/admin/trabajos/{trabajo_id}",
        json=_payload(catalogo, titulo="Título editado"),
        headers=auth_headers,
    )
    assert update.status_code == 200
    assert update.json()["titulo"] == "Título editado"

    delete = client.delete(f"/api/admin/trabajos/{trabajo_id}", headers=auth_headers)
    assert delete.status_code == 204

    assert client.get("/api/trabajos").json() == []


def test_delete_missing_returns_404(client, auth_headers):
    response = client.delete("/api/admin/trabajos/999", headers=auth_headers)
    assert response.status_code == 404


def test_switch_tipo_removes_old_image(client, auth_headers, catalogo):
    created = client.post(
        "/api/admin/trabajos",
        json=_payload(catalogo, tipo="antes_despues", foto_url=None, antes_url="https://x/a.jpg", despues_url="https://x/d.jpg"),
        headers=auth_headers,
    ).json()

    updated = client.put(
        f"/api/admin/trabajos/{created['id']}",
        json=_payload(catalogo, tipo="foto"),
        headers=auth_headers,
    ).json()

    assert updated["tipo"] == "foto"
    assert updated["antes_url"] is None
    assert updated["despues_url"] is None
    assert updated["foto_url"] == "https://example.com/foto.jpg"
