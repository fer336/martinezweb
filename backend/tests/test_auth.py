def test_login_success(client):
    response = client.post("/api/auth/login", json={"username": "admin", "password": "admin1234"})
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_wrong_password(client):
    response = client.post("/api/auth/login", json={"username": "admin", "password": "nope"})
    assert response.status_code == 401


def test_admin_endpoint_requires_token(client):
    response = client.get("/api/admin/trabajos")
    assert response.status_code == 401
