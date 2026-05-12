# MobiTranz

> **Plateforme de paiement numerique pour le transport gabonais**
> Client + Conducteur + Admin + Ministere une seule application.

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green.svg)](https://fastapi.tiangolo.com)
[![Tests](https://img.shields.io/badge/Tests-164%20PASSING-brightgreen.svg)](backend/tests/)
[![License](https://img.shields.io/badge/License-Proprietary-yellow.svg)](LICENSE)

---

## Fonctionnalites

| Module | Description |
|--------|-------------|
| **Auth** | JWT + TOTP 2FA + Biometrie + blacklist Redis |
| **Paiements** | MoovMoney, Airtel Money (async via Celery) |
| **Voice NLP** | Transcription vocale (destination + montant + places) |
| **QR Codes** | QR dynamique signe HMAC, expiration 5 min, usage unique |
| **Horn Detection** | Detection klaxon accept/refus par FFT (librosa) |
| **Camera** | Flux video chiffre AES-256-GCM |
| **Notifications** | Push FCM (Android/iOS) via OAuth2 |
| **SMS** | Africa's Talking API pour reset password |
| **Analytics** | KPIs temps reel, rapport ministere CSV |
| **Zones** | 7 zones tarifaires Libreville (PK5, Owendo, Akanda...) |
| **WebSocket** | Temps reel GPS, statuts, incidents (auth JWT) |
| **Audit** | Journal append-only avec hash chain SHA-256 |
| **Monitoring** | Prometheus + Grafana + Sentry |

---

## Architecture

```
nginx (reverse proxy TLS 1.3)
  |
  +-- /api/v1/* -> FastAPI backend (:8000)
  |     +-- Routers (10) -> Services (15) -> Models (13)
  |     +-- WebSocket (auth JWT)
  |     +-- Celery Worker (file attente asynchrone)
  |
  +-- PostgreSQL 15 + Redis 7
  +-- Prometheus + Grafana
  +-- MinIO (stockage videos)

Clients:
  +-- Mobile App (Kivy/KivyMD - 19 ecrans)
  +-- Vehicle Device (Raspberry Pi - 6 ecrans)
  +-- Desktop Admin (CustomTkinter - 10 modules)
  +-- PHP Admin Panel (fallback web)
  +-- Ministry Dashboard (Dash/Plotly)
```

---

## Structure

```
mobitranz/
  backend/                  # FastAPI API
    routers/               # 10 endpoints routers
    services/              # 15 services metier
    tasks/                 # 3 taches Celery
    models/                # 13 modeles SQLAlchemy
    schemas/               # Schemas Pydantic
    deps/                  # Dependances auth
    middleware/            # Rate limiting Redis + securite
    scripts/               # Seed DB
    tests/                 # 164 tests fonctionnels
  mobile/                  # Kivy Mobile App
    screens/               # 19 ecrans
  desktop_admin/           # CustomTkinter Windows 11
  vehicle_device/          # App tablette vehicule (Pi)
  ministry_dashboard/      # Dash Plotly ministere
  php_admin/               # Panneau admin PHP
  alembic/                 # Migrations DB (5 revisions)
  tasks/                   # Taches Celery
  shared/                  # Client API partage
  docker-compose.yml       # Dev
  docker-compose.prod.yml  # Production
  pyproject.toml           # Config Python standard
```

---

## Installation

### Pre-requis
- Python 3.12+
- Docker Desktop (PostgreSQL + Redis)
- ffmpeg (horn detection)

### 1. Cloner
```bash
git clone https://github.com/ggboyykxz/mobitranz.git
cd mobitranz
```

### 2. Base de donnees
```bash
docker compose up -d postgres redis
```

### 3. Dependances
```bash
pip install -r requirements/requirements-backend.txt
```

### 4. Variables d'environnement
```bash
cp .env.example .env
```

### 5. Migrations
```bash
alembic upgrade head
```

### 6. Seed
```bash
python backend/scripts/seed.py
```

### 7. Lancer l'API
```bash
uvicorn backend.main:app --reload --port 8000
```

---

## Lancement rapide (tout Docker)

```bash
docker compose up -d
```

---

## Tests

```bash
pytest backend/tests/ -v
pytest backend/tests/ --cov=backend --cov-report=term
pytest backend/tests/test_auth.py -v
```

**Resultat : 164/164 PASSING**

---

## API Endpoints

Tous les endpoints sont prefixes par `/api/v1/`.

| Route | Methode | Auth | Description |
|-------|--------|------|-------------|
| `/auth/login` | POST | - | Connexion |
| `/auth/register` | POST | - | Inscription |
| `/auth/refresh` | POST | - | Rafraichir tokens |
| `/auth/logout` | POST | JWT | Deconnexion (blacklist) |
| `/auth/totp/setup` | GET | JWT | Generer secret TOTP |
| `/auth/password-reset/request` | POST | - | Demande reset SMS |
| `/trips/` | POST | JWT | Creer trajet |
| `/trips/{id}` | GET | JWT | Details trajet |
| `/trips/{id}/join` | POST | JWT | Rejoindre trajet |
| `/trips/{id}/horn` | POST | JWT | Valider klaxon |
| `/payments/initiate` | POST | JWT | Initier paiement |
| `/payments/webhook` | POST | - | Webhook MoovMoney/Airtel |
| `/voice/proposal` | POST | JWT | Proposition vocale |
| `/voice/transcribe` | POST | JWT | Transcrire audio |
| `/drivers/available` | GET | JWT | Conducteurs disponibles |
| `/vehicles/register` | POST | JWT | Enregistrer vehicule |
| `/incidents/report` | POST | JWT | Signaler incident |
| `/admin/dashboard/kpis` | GET | Admin | KPIs temps reel |
| `/admin/logs` | GET | Admin | Audit logs (hash chain) |
| `/analytics/kpis` | GET | JWT | KPIs temps reel |
| `/analytics/ministry-report` | GET | JWT | Rapport ministere |
| `/ws/{channel}` | WS | JWT (query) | WebSocket temps reel |

---

## Identifiants (apres seed)

```
=== ADMIN ===
+24101020304  / AdminMobitranz2026!
+24102030405  / SuperAdmin2026!

=== MINISTERE ===
+24103040506  / Ministere2026!

=== CONDUCTEURS ===
+24106010203  / DriverJean2026!
+24106102030  / DriverMarie2026!
+24106203040  / DriverPaul2026!

=== CLIENT ===
+24107010203  / ClientTest2026!
```

---

## Variables d'environnement requises

```
SECRET_KEY=<cle 32 bytes aleatoire>
JWT_SECRET=<cle 32 bytes>
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db
REDIS_URL=redis://host:6379/0
CORS_ORIGINS=http://localhost:3000,https://app.mobitranz.ga

# Optionnel
SENTRY_DSN=https://...
AFRICASTALKING_API_KEY=...
AFRICASTALKING_USERNAME=...
FIREBASE_CREDENTIALS_PATH=...
MOOVMONEY_API_URL=...
AIRTELMONEY_API_URL=...
```

---

## Taches asynchrones (Celery)

```bash
# Lancer le worker
celery -A backend.tasks.celery_app worker --loglevel=info --concurrency=4

# Lancer le beat (taches periodiques)
celery -A backend.tasks.celery_app beat --loglevel=info
```

---

## Docker Production

```bash
docker compose -f docker-compose.prod.yml up -d
```

---

## Developpement

```bash
ruff check backend/ --fix
ruff format backend/
mypy backend/
pytest backend/tests/ --cov=backend
```

---

## Licence

Proprietaire 2026 MobiTranz Gabon