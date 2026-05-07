# MobiTranz — Documentation des Agents et Automatisations

Ce fichier documente les agents, scripts et automatisations disponibles pour le projet MobiTranz.

---

## Agents Disponibles

### 1. Agent Audit et Corrections

**Description**: Analyse le projet et corrige les bugs identifiés.

**Commande**:
```
/audit
```

**Fonctionnalités**:
- Analyse syntaxique de tous les fichiers Python
- Vérification des imports et dépendances
- Exécution des tests unitaires
- Correction automatique des erreurs triviales
- Rapport des problèmes non résolus

---

### 2. Agent Tests

**Description**: Exécute et génère des rapports de tests.

**Commande**:
```
/test [fichier|module]
```

**Fonctionnalités**:
- Exécution des tests pytest
- Génération de rapport de couverture
- Tests unitaires, intégration et sécurité
- Vérification du taux de couverture (>80%)

---

### 3. Agent Documentation

**Description**: Génère et met à jour la documentation.

**Commande**:
```
/docs
```

**Fonctionnalités**:
- Génération docstrings manquantes
- Création README pour chaque module
- Export documentation API
- Vérification conformité cahier des charges

---

### 4. Agent Sécurité

**Description**: Analyse les vulnérabilités de sécurité.

**Commande**:
```
/security
```

**Fonctionnalités**:
- Scan injection SQL
- Vérification authentification
- Analyse des dépendances vulnérables
- Audit des tokens et clés

---

## Scripts de Développement

### Linting

```bash
# Linting Python
python -m flake8 backend/ --max-line-length=100
python -m black backend/ --check
python -m mypy backend/
```

### Tests

```bash
# Tous les tests
python -m pytest backend/tests/ -v

# Couverture
python -m pytest backend/tests/ --cov=backend --cov-report=html
```

### Démarrage

```bash
# Backend FastAPI
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# App Mobile (nécessite buildozer)
buildozer android debug

# App Desktop Admin
python desktop_admin/main.py

# Raspberry Pi Vehicle
python vehicle_device/main.py
```

---

## Commandes Utiles

| Commande | Description |
|----------|-------------|
| `/audit` | Analyse et corrige les bugs |
| `/test` | Exécute les tests |
| `/docs` | Génère la documentation |
| `/security` | Scan de sécurité |
| `git status` | Vérifie les modifications |
| `git commit -m "fix: ..."` | Commit avec Conventional Commits |

---

## Patterns de Développement

### Ajouter un nouveau router

1. Créer `backend/routers/nouveau_module.py`
2. Implémenter les endpoints avec documentation
3. Ajouter les imports dans `backend/main.py`
4. Créer les tests dans `backend/tests/test_nouveau_module.py`

### Ajouter un nouveau service

1. Créer `backend/services/mon_service.py`
2. Implémenter la classe de service
3. Ajouter les modèles si nécessaire
4. Exposer via un router

### Ajouter un écran mobile

1. Créer `mobile/screens/role/nom_ecran.py`
2. Implémenter la classe KivyScreen
3. Ajouter dans `mobile/main.py` ScreenManager

---

## Déploiement

### Docker

```bash
# Construction image
docker build -t mobitranz/backend:latest .

# Lancement avec docker-compose
docker-compose up -d
```

### Production

```bash
# Migration base de données
alembic upgrade head

# Démarrage uvicorn avec workers
uvicorn backend.main:app --workers 4 --host 0.0.0.0 --port 8000
```

---

## Monitoring

- **Prometheus**: Métriques sur `http://localhost:9090`
- **Grafana**: Dashboard sur `http://localhost:3000`
- **Logs**: Structurés JSON, niveau configurable via `LOG_LEVEL`