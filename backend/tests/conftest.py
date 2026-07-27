import os

import bcrypt

TEST_PASSWORD = "admin1234"

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["ADMIN_USERNAME"] = "admin"
os.environ["JWT_SECRET"] = "test-secret"
os.environ["ADMIN_PASSWORD_HASH"] = bcrypt.hashpw(TEST_PASSWORD.encode(), bcrypt.gensalt()).decode()

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.db import Base, get_db
from app.main import _general_storage, app
from app.models import Categoria, Zona
from app.rate_limit import limiter
from app.routers.auth import _failed_logins

engine = create_async_engine("sqlite+aiosqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


@pytest_asyncio.fixture(autouse=True)
async def _reset_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(autouse=True)
def _reset_rate_limiter():
    # Sin esto, el estado de rate limiting (in-memory, vive en el proceso) se
    # arrastra entre tests y un test puede empezar a fallar con 429 solo
    # porque otro test anterior ya gastó parte de la cuota o de los intentos
    # fallidos de login.
    limiter.reset()
    _general_storage.reset()
    _failed_logins.clear()


async def _override_get_db():
    async with TestSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = _override_get_db


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_headers(client):
    response = client.post("/api/auth/login", json={"username": "admin", "password": TEST_PASSWORD})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def catalogo():
    async with TestSessionLocal() as session:
        categoria = Categoria(nombre="Plomería y gas")
        zona = Zona(nombre="Pinamar")
        session.add_all([categoria, zona])
        await session.commit()
        await session.refresh(categoria)
        await session.refresh(zona)
        return {"categoria_id": categoria.id, "zona_id": zona.id}
