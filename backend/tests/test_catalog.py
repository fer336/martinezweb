def test_create_categoria(client, auth_headers):
    response = client.post("/api/admin/categorias", json={"nombre": "Instalaciones eléctricas"}, headers=auth_headers)
    assert response.status_code == 201
    assert response.json()["nombre"] == "Instalaciones eléctricas"

    listado = client.get("/api/admin/categorias", headers=auth_headers)
    assert any(c["nombre"] == "Instalaciones eléctricas" for c in listado.json())


def test_create_categoria_duplicada_rechazada(client, auth_headers, catalogo):
    # catalogo ya crea la categoría "Plomería y gas"
    response = client.post("/api/admin/categorias", json={"nombre": "Plomería y gas"}, headers=auth_headers)
    assert response.status_code == 409


def test_create_categoria_vacia_rechazada(client, auth_headers):
    response = client.post("/api/admin/categorias", json={"nombre": "   "}, headers=auth_headers)
    assert response.status_code == 422


def test_categorias_requires_auth(client):
    response = client.post("/api/admin/categorias", json={"nombre": "x"})
    assert response.status_code == 401
