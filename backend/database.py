from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from backend.config import settings

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
)

# Fabricant de sessions async
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Alias pour les scripts
async_session = AsyncSessionLocal

# Base pour les modèles SQLAlchemy
Base = declarative_base()


async def get_db():
    """Générateur de session de base de données."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialise la base de données - crée toutes les tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db():
    """Supprime toutes les tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
