#!/bin/bash
# Backup script for AI Test Case Generator
# This script backs up database, uploaded files, and knowledge base

set -e  # Exit on error

# Configuration
BACKUP_DIR="${BACKUP_DIR:-/var/backups/ai-test-case-generator}"
APP_DIR="${APP_DIR:-/var/www/ai-test-case-generator}"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS="${RETENTION_DAYS:-7}"

# Database configuration
DB_NAME="${DB_NAME:-ai_test_case_generator}"
DB_USER="${DB_USER:-ai_user}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" >&2
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

# Create backup directory
mkdir -p "$BACKUP_DIR"

log "Starting backup process..."

# 1. Backup PostgreSQL database
log "Backing up PostgreSQL database..."
if command -v pg_dump &> /dev/null; then
    PGPASSWORD="$DB_PASSWORD" pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" "$DB_NAME" \
        > "$BACKUP_DIR/db_$DATE.sql"
    
    if [ $? -eq 0 ]; then
        log "Database backup completed: db_$DATE.sql"
        # Compress database backup
        gzip "$BACKUP_DIR/db_$DATE.sql"
        log "Database backup compressed: db_$DATE.sql.gz"
    else
        error "Database backup failed"
        exit 1
    fi
else
    error "pg_dump not found. Please install PostgreSQL client."
    exit 1
fi

# 2. Backup uploaded files
log "Backing up uploaded files..."
if [ -d "$APP_DIR/backend/uploads" ]; then
    tar -czf "$BACKUP_DIR/uploads_$DATE.tar.gz" -C "$APP_DIR/backend" uploads
    if [ $? -eq 0 ]; then
        log "Uploads backup completed: uploads_$DATE.tar.gz"
    else
        warning "Uploads backup failed"
    fi
else
    warning "Uploads directory not found: $APP_DIR/backend/uploads"
fi

# 3. Backup knowledge base
log "Backing up knowledge base..."
if [ -d "$APP_DIR/backend/knowledge_base" ]; then
    tar -czf "$BACKUP_DIR/knowledge_base_$DATE.tar.gz" -C "$APP_DIR/backend" knowledge_base
    if [ $? -eq 0 ]; then
        log "Knowledge base backup completed: knowledge_base_$DATE.tar.gz"
    else
        warning "Knowledge base backup failed"
    fi
else
    warning "Knowledge base directory not found: $APP_DIR/backend/knowledge_base"
fi

# 4. Backup configuration files
log "Backing up configuration files..."
mkdir -p "$BACKUP_DIR/config_$DATE"
cp "$APP_DIR/backend/.env" "$BACKUP_DIR/config_$DATE/.env" 2>/dev/null || warning ".env file not found"
cp -r "$APP_DIR/backend/agent_prompts" "$BACKUP_DIR/config_$DATE/" 2>/dev/null || warning "agent_prompts directory not found"
tar -czf "$BACKUP_DIR/config_$DATE.tar.gz" -C "$BACKUP_DIR" "config_$DATE"
rm -rf "$BACKUP_DIR/config_$DATE"
log "Configuration backup completed: config_$DATE.tar.gz"

# 5. Create backup manifest
log "Creating backup manifest..."
cat > "$BACKUP_DIR/manifest_$DATE.txt" <<EOF
Backup Date: $(date)
Backup Directory: $BACKUP_DIR
Application Directory: $APP_DIR
Database: $DB_NAME

Files:
$(ls -lh "$BACKUP_DIR"/*_$DATE.* 2>/dev/null || echo "No backup files found")

Total Size: $(du -sh "$BACKUP_DIR" | cut -f1)
EOF

log "Backup manifest created: manifest_$DATE.txt"

# 6. Clean up old backups
log "Cleaning up old backups (older than $RETENTION_DAYS days)..."
find "$BACKUP_DIR" -name "db_*.sql.gz" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "uploads_*.tar.gz" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "knowledge_base_*.tar.gz" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "config_*.tar.gz" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "manifest_*.txt" -mtime +$RETENTION_DAYS -delete

log "Old backups cleaned up"

# 7. Calculate total backup size
TOTAL_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
log "Backup completed successfully!"
log "Total backup size: $TOTAL_SIZE"
log "Backup location: $BACKUP_DIR"

# Optional: Send notification
# You can add email, Slack, or other notification methods here
# Example: echo "Backup completed: $TOTAL_SIZE" | mail -s "Backup Success" admin@example.com

exit 0
