#!/bin/bash
# Backup MariaDB database

set -e

# LOAD ENVIRONMENT VARIABLES
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# SET BACKUP DIRECTORY
BACKUP_DIR="./data/backups"
mkdir -p "$BACKUP_DIR"

# GENERATE BACKUP FILENAME
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/song_scanner_$DATE.sql"

echo "Backing up database..."

# CHECK IF RUNNING IN DOCKER
if command -v docker &> /dev/null && docker ps | grep -q scanner-mariadb; then
    echo "Using Docker to backup..."
    docker exec scanner-mariadb mysqldump \
        -u"${MARIADB_USERNAME:-scanner_bot}" \
        -p"${MARIADB_PASSWORD}" \
        --single-transaction \
        --routines \
        --triggers \
        "${MARIADB_DATABASE:-song_scanner}" > "$BACKUP_FILE"
else
    echo "Using local MySQL client to backup..."
    mysqldump \
        -h "${MARIADB_HOST:-localhost}" \
        -P "${MARIADB_PORT:-3306}" \
        -u"${MARIADB_USERNAME:-scanner_bot}" \
        -p"${MARIADB_PASSWORD}" \
        --single-transaction \
        --routines \
        --triggers \
        "${MARIADB_DATABASE:-song_scanner}" > "$BACKUP_FILE"
fi

# COMPRESS BACKUP
echo "Compressing backup..."
gzip "$BACKUP_FILE"

# REMOVE OLD BACKUPS (KEEP LAST 30 DAYS)
echo "Cleaning old backups..."
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +30 -delete

echo ""
echo "✅ Backup completed: ${BACKUP_FILE}.gz"
echo "   Size: $(du -h ${BACKUP_FILE}.gz | cut -f1)"
