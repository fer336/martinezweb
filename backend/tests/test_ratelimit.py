def test_general_rate_limit_returns_429(client):
    for _ in range(60):
        response = client.get("/api/health")
        assert response.status_code == 200
    response = client.get("/api/health")
    assert response.status_code == 429


def test_login_rate_limit_per_ip_returns_429(client):
    # Usuarios distintos en cada intento: aísla el rate limit por IP
    # (10/minuto) del lockout por usuario (5 intentos fallidos/15 min).
    for i in range(10):
        response = client.post("/api/auth/login", json={"username": f"user{i}", "password": "wrong"})
        assert response.status_code == 401
    response = client.post("/api/auth/login", json={"username": "user10", "password": "wrong"})
    assert response.status_code == 429


def test_login_lockout_per_user_after_failed_attempts(client):
    for _ in range(5):
        response = client.post("/api/auth/login", json={"username": "admin", "password": "wrong"})
        assert response.status_code == 401
    response = client.post("/api/auth/login", json={"username": "admin", "password": "admin1234"})
    assert response.status_code == 429
