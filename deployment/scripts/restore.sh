#!/bin/bash
# Restore script for AI Test Case Generator
# This script restores database, uploaded files, and knowledge base from backup

set -e  # Exit on error

# Configuration
BACKUP_DIR="${BACKUP_DIR:-/var/backups/ai-test-case-generator}"
APP_DIR="${APP_DIR:-/var/www/ai-test-case-generator}"

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

# Check if backup directory exists
if [ ! -d "$BACKUP_DIR" ]; then
    error "Backup directory not found: $BACKUP_DIR"
    exit 1
fi

# List available backups
log "Available backups:"
ls -lh "$BACKUP_DIR"/db_*.sql.gz 2>/dev/null | tail -5 || echo "No database backups found"

# Prompt for backup date
echo ""
read -p "Enter backup date (YYYYMMDD_HHMMSS) or 'latest' for most recent: " BACKUP_DATE

if [ "$BACKUP_DATE" = "latest" ]; then
    BACKUP_DATE=$(ls -1 "$BACKUP_DIR"/db_*.sql.gz 2>/dev/null | tail -1 | sed 's/.*db_\(.*\)\.sql\.gz/\1/')
    if [ -z "$BACKUP_DATE" ]; then
        error "No backups found"
        exit 1
    fi
    log "Using latest backup: $BACKUP_DATE"
fi

# Confirm restore
echo ""
warning "This will restore data from backup: $BACKUP_DATE"
warning "Current data will be OVERWRITTEN!"
read -p "Are you sure you want to continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    log "Restore cancelled"
    exit 0
fi

log "Starting restore process..."

# 1. Stop the application
log "Stopping application..."
if command -v systemctl &> /dev/null; then
    sudo systemctl stop ai-test-case-generator 2>/dev/null || warning "Could not stop service"
fi

# 2. Restore database
log "Restoring PostgreSQL database..."
DB_BACKUP="$BACKUP_DIR/db_$BACKUP_DATE.sql.gz"

if [ -f "$DB_BACKUP" ]; then
    # Drop and recreate database
    warning "Dropping existing database..."
    PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres \
        -c "DROP DATABASE IF EXISTS $DB_NAME;"
    
    PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres \
        -c "CREATE DATABASE $DB_NAME;"
    
    # Restore database
    log "Restoring database from backup..."
    gunzip -c "$DB_BACKUP" | PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" "$DB_NAME"
    
    if [ $? -eq 0 ]; then
        log "Database restored successfully"
    else
        error "Database restore failed"
        exit 1
    fi
else
    error "Database backup not found: $DB_BACKUP"
    exit 1
fi

# 3. Restore uploaded files
log "Restoring uploaded files..."
UPLOADS_BACKUP="$BACKUP_DIR/uploads_$BACKUP_DATE.tar.gz"

if [ -f "$UPLOADS_BACKUP" ]; then
    # Backup current uploads
    if [ -d "$APP_DIR/backend/uploads" ]; then
        mv "$APP_DIR/backend/uploads" "$APP_DIR/backend/uploads.old.$(date +%s)"
    fi
    
    # Extract backup
    tar -xzf "$UPLOADS_BACKUP" -C "$APP_DIR/backend"
    
    if [ $? -eq 0 ]; then
        log "Uploads restored successfully"
        # Fix permissions
        chown -R www-data:www-data "$APP_DIR/backend/uploads"
    else
        error "Uploads restore failed"
    fi
else
    warning "Uploads backup not found: $UPLOADS_BACKUP"
fi

# 4. Restore knowledge base
log "Restoring knowledge base..."
KB_BACKUP="$BACKUP_DIR/knowledge_base_$BACKUP_DATE.tar.gz"

if [ -f "$KB_BACKUP" ]; then
    # Backup current knowledge base
    if [ -d "$APP_DIR/backend/knowledge_base" ]; then
        mv "$APP_DIR/backend/knowledge_base" "$APP_DIR/backend/knowledge_base.old.$(date +%s)"
    fi
    
    # Extract backup
    tar -xzf "$KB_BACKUP" -C "$APP_DIR/backend"
    
    if [ $? -eq 0 ]; then
        log "Knowledge base restored successfully"
        # Fix permissions
        chown -R www-data:www-data "$APP_DIR/backend/knowledge_base"
    else
        error "Knowledge base restore failed"
    fi
else
    warning "Knowledge base backup not found: $KB_BACKUP"
fi

# 5. Restore configuration files (optional)
log "Restoring configuration files..."
CONFIG_BACKUP="$BACKUP_DIR/config_$BACKUP_DATE.tar.gz"

if [ -f "$CONFIG_BACKUP" ]; then
    read -p "Do you want to restore configuration files? (yes/no): " RESTORE_CONFIG
    
    if [ "$RESTORE_CONFIG" = "yes" ]; then
        # Extract to temp directory
        TEMP_DIR=$(mktemp -d)
        tar -xzf "$CONFIG_BACKUP" -C "$TEMP_DIR"
        
        # Backup current .env
        if [ -f "$APP_DIR/backend/.env" ]; then
            cp "$APP_DIR/backend/.env" "$APP_DIR/backend/.env.old.$(date +%s)"
        fi
        
        # Restore .env
        cp "$TEMP_DIR/config_$BACKUP_DATE/.env" "$APP_DIR/backend/.env"
        
        # Restore agent_prompts
        if [ -d "$TEMP_DIR/config_$BACKUP_DATE/agent_prompts" ]; then
            rm -rf "$APP_DIR/backend/agent_prompts"
            cp -r "$TEMP_DIR/config_$BACKUP_DATE/agent_prompts" "$APP_DIR/backend/"
        fi
        
        # Clean up
        rm -rf "$TEMP_DIR"
        
        log "Configuration files restored"
    fi
else
    warning "Configuration backup not found: $CONFIG_BACKUP"
fi

# 6. Start the application
log "Starting application..."
if command -v systemctl &> /dev/null; then
    sudo systemctl start ai-test-case-generator
    sleep 5
    sudo systemctl status ai-test-case-generator
fi

log "Restore completed successfully!"
log "Please verify the application is working correctly"

# Optional: Send notification
# echo "Restore completed from backup: $BACKUP_DATE" | mail -s "Restore Success" admin@example.com

exit 0
