# MobiTranz Documentation des Agents et Automatisations

---

## Commandes Disponibles

| Commande | Description |
|----------|-------------|
| `/audit` | Analyse et corrige les bugs |
| `/test [fichier]` | Execute les tests (option: fichier specifique) |
| `/docs` | Met a jour la documentation |
| `/security` | Scan de securite |

---

## Scripts de Developpement

### Linting (via pyproject.toml)
```bash
ruff check backend/
ruff format backend/
mypy backend/
```

### Tests
```bash
pytest backend/tests/ -v
pytest backend/tests/ --cov=backend --cov-report=html
pytest backend/tests/test_auth.py -v
```

### Demarrage
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
celery -A backend.tasks.celery_app worker --loglevel=info
python desktop_admin/main.py
python mobile/main.py
python vehicle_device/main.py
```

---

## Patterns de Developpement

### Ajouter un nouveau router
1. Creer `backend/routers/nouveau_module.py`
2. Implementer les endpoints avec `Depends(get_current_user)` pour la securite
3. Ajouter dans `backend/main.py` avec prefix `/api/v1/`
4. Creer les tests dans `backend/tests/test_nouveau_module.py`

### Ajouter un nouveau service
1. Creer `backend/services/mon_service.py`
2. Implementer la classe avec structlog
3. Exposer via un routeur avec Pydantic schemas

### Ajouter une tache Celery
1. Creer `backend/tasks/mon_task.py`
2. Decorator `@celery_app.task(bind=True, max_retries=3)`
3. Appeler avec `ma_task.delay(...)`

---

## API

Tous les endpoints sont prefixes par `/api/v1/`.

Documentation Swagger : `http://localhost:8000/docs`

---

## Monitoring

- **Prometheus**: `http://localhost:9090`
- **Grafana**: `http://localhost:3000` (admin / ${GRAFANA_PASSWORD})
- **Sentry**: Configure via SENTRY_DSN
- **Logs**: Structlog JSON, niveau via LOG_LEVEL

---

## Infrastructure

```bash
# Dev
docker compose up -d

# Production
docker compose -f docker-compose.prod.yml up -d

# Migrations
alembic upgrade head

# Seed
python backend/scripts/seed.py
```