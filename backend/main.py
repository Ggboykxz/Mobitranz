# ============================================================
# Point d'entrée FastAPI MobiTranz
# Fichier : backend/main.py
# Description : Application FastAPI principale
# ============================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.docs import Redoc
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import structlog
from contextlib import asynccontextmanager

from backend.config import settings
from backend.database import init_db, engine
from backend.redis_client import redis_client

# ============================================================
# Configuration OpenAPI
# ============================================================
openapi_tags = [
    {"name": "Auth", "description": "Authentification et gestion des tokens"},
    {"name": "Trips", "description": "Gestion des trajets"},
    {"name": "Payments", "description": "Paiements et transactions"},
    {"name": "Drivers", "description": "Gestion des chauffeurs"},
    {"name": "Vehicles", "description": "Gestion des véhicules"},
    {"name": "Voice", "description": "Reconnaissance vocale et propositions"},
    {"name": "Incidents", "description": "Signalement et gestion des incidents"},
    {"name": "Analytics", "description": "Statistiques et rapports"},
    {"name": "Users", "description": "Gestion des utilisateurs"},
    {"name": "Admin", "description": "Fonctions d'administration"},
    {"name": "Health", "description": "Vérifications de santé"},
]

# Import routers
from backend.routers import (
    auth,
    trips,
    payments,
    drivers,
    vehicles,
    voice,
    incidents,
    analytics,
    users,
    admin,
)

# Import WebSocket
from backend.websocket import websocket_router

# Import Middleware
from backend.middleware.security import SecurityHeadersMiddleware, RateLimitMiddleware

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestionnaire du cycle de vie de l'application."""
    logger.info("Démarrage de MobiTranz", version=settings.app_version)

    try:
        logger.info("Initialisation de la base de données")
        await init_db()
    except Exception as e:
        logger.warning("Base de données non disponible", error=str(e))

    try:
        logger.info("Connexion à Redis")
        await redis_client.connect()
    except Exception as e:
        logger.warning("Redis non disponible", error=str(e))

    yield

    try:
        logger.info("Fermeture des connexions")
        await redis_client.disconnect()
        await engine.dispose()
    except Exception:
        pass

    logger.info("MobiTranz arrêté")


app = FastAPI(
    title="MobiTranz API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    description="""## MobiTranz - Plateforme de Paiement Numérique pour le Transport Gabonais

### Fonctionnalités

- **Authentification** : Inscription, connexion, JWT tokens, 2FA TOTP
- **Gestion des Trajets** : Création, suivi, historique des trajets
- **Paiements** : MoovMoney, Airtel Money, Wallet numérique, QR codes
- **Chauffeurs** : Gestion des chauffeurs et de leur statut
- **Véhicules** : Suivi GPS et gestion des véhicules
- **Incidents** : Signalement et gestion des incidents (SOS)
- **Analytiques** : Statistiques et rapportsministère
- **Vocabulaire** : Analyse vocale pour propositions de trajets
- **Administration** : CRUD complet pour tous les modules
- **WebSocket** : Temps réel pour GPS, notifications, incidents

### Authentification

Tous les endpoints protégés nécessitent un token JWT dans le header:
```
Authorization: Bearer <token>
```

### Rate Limiting

- Auth endpoints: 5 requêtes / 15 min
- Paiements: 10 requêtes / min
- API générale: 100 requêtes / min

### Contact

- **Email**: support@mobitranz.ga
- **Site**: https://mobitranz.ga
- **Pays**: Gabon (Libreville)
- **Version API**: v1
""",
    license_info={
        "name": "Propriétaire - MobiTranz Gabon",
        "url": "https://mobitranz.ga/legal"
    },
    contact={
        "name": "Support MobiTranz",
        "email": "support@mobitranz.ga",
        "url": "https://mobitranz.ga/support"
    },
    lifespan=lifespan,
    openapi_url="/openapi.json",
    openapi_tags=openapi_tags,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=100)


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
app.include_router(websocket_router, tags=["WebSocket"])


@app.get("/")
async def root():
    """Route racine."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "online",
    }


@app.get("/health")
async def health():
    """Vérification de l'état de santé."""
    health_status = {"status": "healthy", "services": {}}

    # Check database
    try:
        from sqlalchemy import text

        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        health_status["services"]["database"] = "ok"
    except Exception as e:
        health_status["services"]["database"] = f"error: {str(e)}"
        health_status["status"] = "degraded"

    # Check Redis
    try:
        if redis_client.redis:
            await redis_client.redis.ping()
            health_status["services"]["redis"] = "ok"
    except Exception as e:
        health_status["services"]["redis"] = f"error: {str(e)}"
        health_status["status"] = "degraded"

    return health_status


logger.info("Application MobiTranz initialisée")
