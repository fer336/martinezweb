def test_get_config_default_is_null(client):
    response = client.get("/api/config")
    assert response.status_code == 200
    assert response.json() == {"hero_image_url": None}


def test_update_config_requires_auth(client):
    response = client.put("/api/admin/config", json={"hero_image_url": "https://x/y.jpg"})
    assert response.status_code == 401


def test_update_and_read_config(client, auth_headers):
    update = client.put("/api/admin/config", json={"hero_image_url": "https://x/hero.jpg"}, headers=auth_headers)
    assert update.status_code == 200
    assert update.json()["hero_image_url"] == "https://x/hero.jpg"

    public = client.get("/api/config")
    assert public.json()["hero_image_url"] == "https://x/hero.jpg"
