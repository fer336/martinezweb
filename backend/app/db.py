from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

# pool_size/max_overflow son propios de QueuePool: el engine sqlite en
# memoria de los tests usa StaticPool y la creación del engine falla si se
# los pasamos, así que solo se aplican contra Postgres.
_engine_kwargs: dict[str, object] = {
    # Valida la conexión (SELECT 1) antes de entregarla del pool; si el
    # servidor ya la cerró, la descarta y abre una nueva en vez de fallar
    # en medio de la query (asyncpg.ConnectionDoesNotExistError).
    "pool_pre_ping": True,
    # Recicla conexiones con más de 30 min: evita que el pool retenga
    # conexiones que un firewall/proxy intermedio o la propia DB puedan
    # cortar por idle timeout.
    "pool_recycle": 1800,
}
if settings.database_url.startswith("postgresql"):
    _engine_kwargs["pool_size"] = 5
    _engine_kwargs["max_overflow"] = 10

engine = create_async_engine(settings.database_url, **_engine_kwargs)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session
