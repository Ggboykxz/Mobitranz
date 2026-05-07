# ============================================================
# Point d'entrée FastAPI MobiTranz
# Fichier : backend/main.py
# Description : Application FastAPI principale
# ============================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import structlog
from contextlib import asynccontextmanager

from backend.config import settings
from backend.database import init_db, engine
from backend.redis_client import redis_client

# Import routers
from backend.routers import auth, trips, payments, drivers, vehicles, voice, incidents, analytics, users, admin


logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestionnaire du cycle de vie de l'application."""
    logger.info("Démarrage de MobiTranz", version=settings.app_version)
    
    logger.info("Initialisation de la base de données")
    await init_db()
    
    logger.info("Connexion à Redis")
    await redis_client.connect()
    
    yield
    
    logger.info("Fermeture des connexions")
    await redis_client.disconnect()
    await engine.dispose()
    
    logger.info("MobiTranz arrêté")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Plateforme de paiement numérique pour le transport gabonais",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000", "http://127.0.0.1:3000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# Include routers
app.include_router(auth.router, prefix="/auth")
app.include_router(trips.router, prefix="/trips")
app.include_router(payments.router, prefix="/payments")
app.include_router(drivers.router, prefix="/drivers")
app.include_router(vehicles.router, prefix="/vehicles")
app.include_router(voice.router, prefix="/voice")
app.include_router(incidents.router, prefix="/incidents")
app.include_router(analytics.router, prefix="/analytics")
app.include_router(users.router, prefix="/users")
app.include_router(admin.router, prefix="/admin")


@app.get("/")
async def root():
    """Route racine."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "online"
    }


@app.get("/health")
async def health():
    """Vérification de l'état de santé."""
    return {"status": "healthy"}


logger.info("Application MobiTranz initialisée")