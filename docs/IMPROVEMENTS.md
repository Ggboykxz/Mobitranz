# MobiTranz Prochaines Ameliorations

---

## Realise

### Backend
- [x] WebSocket temps reel (GPS, statuts, incidents)
- [x] Rate limiting Redis (remplace in-memory)
- [x] Headers de securite (CORS, CSP, HSTS)
- [x] Protection CSRF (via utils/security.py)
- [x] Sanitization des entrees
- [x] Limitation des requetes par IP (Redis)
- [x] Endpoint /health complet (DB + Redis + uptime)
- [x] Metriques Prometheus
- [x] Integration Grafana (datasource provisionnee)
- [x] Logging structure JSON (structlog)
- [x] API versioning /api/v1/
- [x] Documentation OpenAPI complete
- [x] Service SMS (Africa's Talking)
- [x] Service Push FCM (Firebase)
- [x] Background tasks Celery + Redis
- [x] Migrations Alembic completes (5 revisions)
- [x] Index optimises (003_indexes.py)
- [x] Requetes paginees
- [x] Audit hash chain SHA-256
- [x] Auth JWT WebSocket
- [x] Blacklist tokens Redis (logout)
- [x] Protection injection SQL (regex)
- [x] FCM v1 OAuth2 (JWT service account)
- [x] Multi-stage Docker + .dockerignore
- [x] pyproject.toml (ruff, mypy, pytest)
- [x] Sentry monitoring
- [x] 164 tests fonctionnels

### Administration
- [x] PHP Admin connecte a l'API reelle
- [x] Dashboard Ministere connecte a l'API reelle
- [x] Credentials hardcodes supprimes
- [x] Session fixation PHP corrigee

### Infrastructure
- [x] Dockerfile optimise multi-stage
- [x] docker-compose dev + prod
- [x] Health checks DB, Redis, Celery
- [x] Grafana provisioning datasource
- [x] Prometheus targets corrects

---

## A Faire

### Phase 1 Court terme

#### Securite
- [ ] Rate limiting WebSocket par IP
- [ ] Validation taille fichiers upload (audio, images)
- [ ] Endpoint de-registration device token FCM
- [ ] Tests de securite automatises (bandit + safety CI)
- [ ] Renouvellement automatique token OAuth2 FCM

#### Tests
- [ ] Tests integration avec test containers PostgreSQL
- [ ] Tests de charge (Locust)
- [ ] Tests E2E WebSocket
- [ ] Couverture > 85%

#### Mobile (Kivy)
- [ ] Mode offline partiel
- [ ] Push notifications FCM
- [ ] Lecture vocale TTS
- [ ] Authentification biometrique
- [ ] Geoloalisation continue

### Phase 2 Moyen terme

#### Backend
- [ ] Cache Redis pour les requetes frequentes (zones, drivers)
- [ ] Pagination curseur pour grandes tables (audit_logs)
- [ ] Export PDF des rapports ministere
- [ ] API de recherche full-text (trigrammes PostgreSQL)
- [ ] Versioning schema BDD (migrations downgrade testees)

#### Infrastructure
- [ ] Manifests Kubernetes (Helm charts)
- [ ] Terraform pour provisioning cloud
- [ ] CI/CD deploiement automatique staging/prod
- [ ] Backup automatise BDD (pg_dump cron)
- [ ] Rate limiting WebSocket par IP
- [ ] Alerting Grafana (email + Slack)

#### Vehicle Device
- [ ] Mode hors-ligne complet avec sync
- [ ] Mise a jour firmware OTA
- [ ] Diagnostic hardware auto

### Phase 3 Long terme

- [ ] Multi-langues (Francais, Anglais, langues locales)
- [ ] Chat temps reel client-conducteur (WebSocket)
- [ ] Chatbot IA pour support client
- [ ] Dashboard conducteur avec analytics personnels
- [ ] Wallet rechargeable avec historique
- [ ] Programme de fidelite
- [ ] API publique pour partenaires
- [ ] Application iOS native (Swift)
- [ ] Paiement par QR code statique commerçant

---

## Priorites

1. Tests integration PostgreSQL
2. Mode offline mobile
3. CI/CD complet
4. Kubernetes / scaling
5. Backup automatise