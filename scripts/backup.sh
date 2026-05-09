#!/bin/bash
# ============================================================
# MobiTranz - Script de Sauvegarde
# ============================================================

BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)
CONTAINER="mobitranz-db"

mkdir -p "$BACKUP_DIR"

echo "📦 Sauvegarde MobiTranz - $DATE"

# Database backup
echo "Sauvegarde PostgreSQL..."
docker exec "$CONTAINER" pg_dump -U mobitranz mobitranz > "$BACKUP_DIR/db_$DATE.sql"
gzip "$BACKUP_DIR/db_$DATE.sql"

# Redis backup
echo "Sauvegarde Redis..."
docker exec mobitranz-redis redis-cli SAVE > /dev/null 2>&1
docker cp mobitranz-redis:/data/dump.rdb "$BACKUP_DIR/redis_$DATE.rdb"

# Keep only last 7 backups
find "$BACKUP_DIR" -name "db_*.sql.gz" -mtime +7 -delete
find "$BACKUP_DIR" -name "redis_*.rdb" -mtime +7 -delete

echo "✅ Sauvegarde terminée: $BACKUP_DIR"
ls -lh "$BACKUP_DIR"