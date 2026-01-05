#!/bin/bash
# Setup MariaDB database for WhatsApp Song Scanner

set -e

echo "Setting up MariaDB database..."

# LOAD ENVIRONMENT VARIABLES
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "Error: .env file not found. Copy .env.example to .env first."
    exit 1
fi

# CHECK IF RUNNING IN DOCKER
if [ -n "$DOCKER_CONTAINER" ]; then
    echo "Running in Docker container..."
    DB_HOST="mariadb"
else
    DB_HOST="${MARIADB_HOST:-localhost}"
fi

# WAIT FOR MARIADB TO BE READY
echo "Waiting for MariaDB to be ready..."
max_attempts=30
attempt=0

while ! mysql -h "$DB_HOST" -P "${MARIADB_PORT:-3306}" -u root -p"${MARIADB_ROOT_PASSWORD}" -e "SELECT 1" >/dev/null 2>&1; do
    attempt=$((attempt + 1))
    if [ $attempt -ge $max_attempts ]; then
        echo "Error: Could not connect to MariaDB after $max_attempts attempts"
        exit 1
    fi
    echo "Waiting for MariaDB... ($attempt/$max_attempts)"
    sleep 2
done

echo "MariaDB is ready!"

# CREATE DATABASE AND USER
echo "Creating database and user..."
mysql -h "$DB_HOST" -P "${MARIADB_PORT:-3306}" -u root -p"${MARIADB_ROOT_PASSWORD}" <<EOF
CREATE DATABASE IF NOT EXISTS ${MARIADB_DATABASE} 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS '${MARIADB_USERNAME}'@'%' 
IDENTIFIED BY '${MARIADB_PASSWORD}';

GRANT ALL PRIVILEGES ON ${MARIADB_DATABASE}.* 
TO '${MARIADB_USERNAME}'@'%';

FLUSH PRIVILEGES;
EOF

echo "✅ Database setup complete!"
echo ""
echo "Database: ${MARIADB_DATABASE}"
echo "User: ${MARIADB_USERNAME}"
echo "Host: $DB_HOST:${MARIADB_PORT:-3306}"
