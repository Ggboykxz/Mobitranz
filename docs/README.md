# MobiTranz 🇬🇦

> **Plateforme de paiement numérique pour le transport gabonais**
>
> Client + Conducteur + Admin + Ministère — une seule application.

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green.svg)](https://fastapi.tiangolo.com)
[![Tests](https://img.shields.io/badge/Tests-76%2F76%20PASSING-brightgreen.svg)](backend/tests/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🎯 Fonctionnalités

| Module | Description |
|--------|-------------|
| **Auth** | JWT + TOTP 2FA + Biométrie |
| **Paiements** | MoovMoney, Airtel Money, Carte, Espèces |
| **Voice NLP** | Transcription vocale (destination + montant + places) |
| **QR Codes** | QR dynamique signé, expiration 5 min |
| **Horn Detection** | Détection klaxon accept/refus par FFT |
| **Camera** | Flux vidéo chiffré AES-256-GCM |
| **Notifications** | Push FCM (Android/iOS) |
| **Analytics** | KPIs temps réel, rapport ministère CSV |
| **Zones** | 7 zones tarifaires Libreville (PK5, Owendo, Akanda...) |

---

## 🗂️ Structure

```
mobitranz/
├── backend/              # FastAPI API
│   ├── routers/         # 9 endpoints routers
│   ├── services/        # 8 services métier
│   ├── models/           # 11 modèles SQLAlchemy
│   ├── schemas/          # Pydantic schemas
│   ├── deps/             # Auth dependencies
│   ├── scripts/          # Seed DB
│   └── tests/            # 76 tests
├── mobile/               # Kivy Mobile App
│   └── screens/          # 17 écrans
├── desktop_admin/        # CustomTkinter Windows 11
│   └── windows/modules/  # 10 modules Fluent
├── vehicle_device/        # App tablette véhicule
├── ministry_dashboard/    # Dash Plotly ministère
├── alembic/              # Migrations DB
├── docker-compose.yml     # PostgreSQL + Redis + MinIO
├── requirements*.txt     # Dépendances splittées
└── nginx.conf           # Reverse proxy SSL
```

---

## 🚀 Installation

### Prérequis
- Python 3.13+
- Docker Desktop (pour PostgreSQL + Redis)
- ffmpeg (pour horn detection)

### 1. Cloner
```bash
git clone https://github.com/ggboyykxz/mobitranz.git
cd mobitranz
```

### 2. Base de données
```bash
docker compose up -d postgres redis
```

### 3. Dépendances
```bash
pip install -r requirements.txt
# ou
pip install -r requirements-backend.txt
pip install -r requirements-services.txt
```

### 4. Variables d'environnement
```bash
cp .env.example .env
# Éditer .env avec vos clés API
```

### 5. Migrations
```bash
cd alembic && alembic upgrade head
```

### 6. Seed (données initiales)
```bash
python backend/scripts/seed.py
```

### 7. Lancer l'API
```bash
uvicorn backend.main:app --reload --port 8000
```

---

## 📱 Mobile

```bash
# Android (APK)
pip install buildozer
buildozer android debug

# Desktop Linux/Mac
python -m mobile.main
```

---

## 🖥️ Desktop Admin

```bash
pip install -r requirements-admin.txt
python desktop_admin/main.py
```

---

## 🐳 Docker

```bash
# Tout infrastructure
docker compose up -d

# Avec API
docker compose --profile api up -d
```

---

## 🧪 Tests

```bash
# Tous les tests
pytest backend/tests/ -v

# Avec coverage
pytest backend/tests/ --cov=backend --cov-report=html --cov-report=term

# Tests d'intégration multi-rôles
pytest backend/tests/test_integration.py -v

# Un fichier
pytest backend/tests/test_auth.py -v
pytest backend/tests/test_voice.py -v
```

**Résultat : 76/76 PASSING**

---

## 🔑 Identifiants (après seed)

```text
=== ADMIN ===
+24101020304  / AdminMobitranz2026!
+24102030405  / SuperAdmin2026!

=== MINISTÈRE ===
+24103040506  / Ministere2026!

=== CONDUCTEURS ===
+24106010203  / DriverJean2026!
+24106102030  / DriverMarie2026!
+24106203040  / DriverPaul2026!

=== CLIENT ===
+24107010203  / ClientTest2026!
```

---

## 🔌 API Endpoints

| Route | Méthode | Description |
|-------|--------|-------------|
| `/auth/login` | POST | Connexion |
| `/auth/register` | POST | Inscription |
| `/auth/totp/setup` | GET | Générer secret TOTP |
| `/auth/logout` | POST | Déconnexion |
| `/auth/password-reset/request` | POST | Demande reset |
| `/trips/` | POST | Créer trajet |
| `/trips/{id}/join` | POST | Rejoindre trajet |
| `/trips/{id}/horn` | POST | Valider klaxon |
| `/payments/initiate` | POST | Initier paiement |
| `/payments/webhook` | POST |Webhook MoovMoney/Airtel |
| `/voice/proposal` | POST | Soumettre proposition vocale |
| `/incidents/report` | POST | Signaler incident |
| `/analytics/kpis` | GET | KPIs temps réel |
| `/analytics/ministry-report` | GET | Rapport ministère |
| `/drivers/available` | GET | Conducteurs disponibles |

---

## ☁️ Déploiement

### Railway / Render
```bash
# Variables requises
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db
REDIS_URL=redis://host:6379/0
SECRET_KEY=<32-bytes-random>
MOOVMONEY_API_URL=https://api.moovmoney.ga/v1
AIRTELMONEY_API_URL=https://api.airtelmoney.ga/v1
```

### VPS (Ubuntu)
```bash
# 1. Installer Docker
# 2. Clone repo
# 3. docker compose up -d
# 4. python backend/scripts/seed.py
# 5. nginx -s reload
```

---

## 📦 Dépendances

| Fichier | Usage |
|---------|-------|
| `requirements-backend.txt` | API FastAPI |
| `requirements-services.txt` | Audio/ML (librosa, scipy) |
| `requirements-admin.txt` | Desktop Admin (CustomTkinter) |
| `requirements-mobile.txt` | Mobile App (Kivy) |

---

## 🛠️ Développement

```bash
# Formatage code
ruff check backend/ --fix
ruff format backend/

# Type checking
mypy backend/

# Lint
ruff check backend/
```

---

## 📄 License

MIT © 2026 MobiTranz Gabon