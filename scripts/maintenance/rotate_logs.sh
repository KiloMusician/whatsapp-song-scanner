#!/bin/bash
# Rotate log files

set -e

echo "Rotating log files..."

LOG_DIR="./data/logs"

if [ ! -d "$LOG_DIR" ]; then
    echo "Log directory not found: $LOG_DIR"
    exit 0
fi

# ROTATE LOGS LARGER THAN 100MB
MAX_SIZE_MB=100
MAX_SIZE_BYTES=$((MAX_SIZE_MB * 1024 * 1024))

for log_file in "$LOG_DIR"/*.log; do
    if [ -f "$log_file" ]; then
        file_size=$(stat -f%z "$log_file" 2>/dev/null || stat -c%s "$log_file" 2>/dev/null)
        
        if [ "$file_size" -gt "$MAX_SIZE_BYTES" ]; then
            timestamp=$(date +%Y%m%d_%H%M%S)
            backup_file="${log_file}.${timestamp}"
            
            echo "Rotating $log_file ($(du -h "$log_file" | cut -f1))"
            mv "$log_file" "$backup_file"
            gzip "$backup_file"
            touch "$log_file"
            
            echo "  → ${backup_file}.gz"
        fi
    fi
done

# REMOVE OLD ROTATED LOGS (KEEP LAST 10)
for base_log in "$LOG_DIR"/*.log; do
    base_name=$(basename "$base_log" .log)
    
    # Count rotated logs for this base
    count=$(ls -1 "$LOG_DIR/${base_name}.log".*.gz 2>/dev/null | wc -l)
    
    if [ "$count" -gt 10 ]; then
        echo "Removing old rotated logs for $base_name (keeping 10 most recent)"
        ls -1t "$LOG_DIR/${base_name}.log".*.gz | tail -n +11 | xargs rm -f
    fi
done

echo ""
echo "✅ Log rotation complete!"
