#!/bin/bash
# ============================================================
# MobiTranz - Script de Sauvegarde
# Usage: ./scripts/backup.sh [db|redis|all]
# ============================================================

BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_CONTAINER="${DB_CONTAINER:-mobitranz-db}"
REDIS_CONTAINER="${REDIS_CONTAINER:-mobitranz-redis}"
RETENTION_DAYS="${RETENTION_DAYS:-7}"
MODE="${1:-all}"

mkdir -p "$BACKUP_DIR"

backup_db() {
    echo "Sauvegarde PostgreSQL..."
    docker exec "$DB_CONTAINER" pg_dump -U mobitranz mobitranz | gzip > "$BACKUP_DIR/db_$DATE.sql.gz" && \
    echo "OK: db_$DATE.sql.gz ($(du -h "$BACKUP_DIR/db_$DATE.sql.gz" | cut -f1))"
}

backup_redis() {
    echo "Sauvegarde Redis..."
    docker exec "$REDIS_CONTAINER" redis-cli SAVE > /dev/null 2>&1
    docker cp "$REDIS_CONTAINER":/data/dump.rdb "$BACKUP_DIR/redis_$DATE.rdb" && \
    echo "OK: redis_$DATE.rdb ($(du -h "$BACKUP_DIR/redis_$DATE.rdb" | cut -f1))"
}

cleanup() {
    find "$BACKUP_DIR" -name "db_*.sql.gz" -mtime +$RETENTION_DAYS -delete
    find "$BACKUP_DIR" -name "redis_*.rdb" -mtime +$RETENTION_DAYS -delete
}

case "$MODE" in
    db) backup_db ;;
    redis) backup_redis ;;
    all) backup_db; backup_redis ;;
esac
cleanup
echo "Sauvegarde terminee: $BACKUP_DIR"