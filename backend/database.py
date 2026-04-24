# ============================================================
# Configuration Base de Données MobiTranz
# Fichier : backend/database.py
# Description : Connexion PostgreSQL avec SQLAlchemy async
# ============================================================

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine
from backend.config import settings


# Création du moteur de base de données async
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)


# Fabricant de sessions async
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# Base pour les modèles SQLAlchemy
Base = declarative_base()


async def get_db():
    """Générateur de session de base de données async.
    
    Utilisation :
        @router.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            ...
    
    Yields:
        AsyncSession: Session de base de données
    """
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
    """Initialise la base de données.
    
    Crée toutes les tables si elles n'existent pas.
    À appeler au démarrage de l'application.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db():
    """Supprime toutes les tables de la base de données.
    
    À utiliser avec précaution en environnement de développement.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)