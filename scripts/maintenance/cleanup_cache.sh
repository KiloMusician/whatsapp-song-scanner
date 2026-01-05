#!/bin/bash
# Clean cache files

set -e

echo "Cleaning cache files..."

# CLEAN REDIS CACHE (IF DOCKER)
if command -v docker &> /dev/null && docker ps | grep -q scanner-redis; then
    echo "Flushing Redis cache..."
    docker exec scanner-redis redis-cli FLUSHDB
    echo "✅ Redis cache flushed"
fi

# CLEAN FILE CACHE
CACHE_DIR="./data/cache"
if [ -d "$CACHE_DIR" ]; then
    echo "Cleaning file cache..."
    rm -rf "$CACHE_DIR"/*
    echo "✅ File cache cleaned"
fi

# CLEAN TEMP FILES
TEMP_DIR="./data/temp"
if [ -d "$TEMP_DIR" ]; then
    echo "Cleaning temp files..."
    rm -rf "$TEMP_DIR"/*
    echo "✅ Temp files cleaned"
fi

# CLEAN PYTHON CACHE
echo "Cleaning Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
echo "✅ Python cache cleaned"

echo ""
echo "✅ Cache cleanup complete!"
