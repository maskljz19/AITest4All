#!/bin/bash
# Monitoring script for AI Test Case Generator
# This script checks the health of all components and sends alerts if needed

set -e

# Configuration
APP_NAME="AI Test Case Generator"
BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"
HEALTH_ENDPOINT="${HEALTH_ENDPOINT:-/health}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-ai_test_case_generator}"
DB_USER="${DB_USER:-ai_user}"
REDIS_HOST="${REDIS_HOST:-localhost}"
REDIS_PORT="${REDIS_PORT:-6379}"

# Alert configuration
ALERT_EMAIL="${ALERT_EMAIL:-}"
ALERT_WEBHOOK="${ALERT_WEBHOOK:-}"  # Slack/Discord webhook URL

# Thresholds
CPU_THRESHOLD="${CPU_THRESHOLD:-80}"
MEMORY_THRESHOLD="${MEMORY_THRESHOLD:-80}"
DISK_THRESHOLD="${DISK_THRESHOLD:-85}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Status tracking
OVERALL_STATUS=0
ISSUES=()

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" >&2
    ISSUES+=("$1")
    OVERALL_STATUS=1
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
    ISSUES+=("WARNING: $1")
}

success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] OK:${NC} $1"
}

# Send alert function
send_alert() {
    local message="$1"
    
    # Send email alert
    if [ -n "$ALERT_EMAIL" ]; then
        echo "$message" | mail -s "[$APP_NAME] Alert" "$ALERT_EMAIL"
    fi
    
    # Send webhook alert (Slack/Discord)
    if [ -n "$ALERT_WEBHOOK" ]; then
        curl -X POST "$ALERT_WEBHOOK" \
            -H 'Content-Type: application/json' \
            -d "{\"text\":\"[$APP_NAME] $message\"}" \
            2>/dev/null
    fi
}

log "Starting health check for $APP_NAME..."

# 1. Check backend service
log "Checking backend service..."
HEALTH_URL="$BACKEND_URL$HEALTH_ENDPOINT"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$HEALTH_URL" --max-time 10)

if [ "$HTTP_CODE" = "200" ]; then
    success "Backend service is healthy (HTTP $HTTP_CODE)"
else
    error "Backend service is unhealthy (HTTP $HTTP_CODE)"
fi

# 2. Check PostgreSQL
log "Checking PostgreSQL..."
if command -v pg_isready &> /dev/null; then
    if pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" > /dev/null 2>&1; then
        success "PostgreSQL is accepting connections"
        
        # Check database size
        DB_SIZE=$(PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
            -t -c "SELECT pg_size_pretty(pg_database_size('$DB_NAME'));" 2>/dev/null | xargs)
        log "Database size: $DB_SIZE"
        
        # Check connection count
        CONN_COUNT=$(PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
            -t -c "SELECT count(*) FROM pg_stat_activity WHERE datname='$DB_NAME';" 2>/dev/null | xargs)
        log "Active connections: $CONN_COUNT"
    else
        error "PostgreSQL is not accepting connections"
    fi
else
    warning "pg_isready not found, skipping PostgreSQL check"
fi

# 3. Check Redis
log "Checking Redis..."
if command -v redis-cli &> /dev/null; then
    if redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" ping > /dev/null 2>&1; then
        success "Redis is responding"
        
        # Check Redis memory
        REDIS_MEMORY=$(redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" info memory | grep used_memory_human | cut -d: -f2 | tr -d '\r')
        log "Redis memory usage: $REDIS_MEMORY"
        
        # Check Redis keys
        REDIS_KEYS=$(redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" dbsize | cut -d: -f2 | tr -d '\r')
        log "Redis keys: $REDIS_KEYS"
    else
        error "Redis is not responding"
    fi
else
    warning "redis-cli not found, skipping Redis check"
fi

# 4. Check system resources
log "Checking system resources..."

# CPU usage
if command -v mpstat &> /dev/null; then
    CPU_USAGE=$(mpstat 1 1 | awk '/Average/ {print 100-$NF}' | cut -d. -f1)
    if [ "$CPU_USAGE" -gt "$CPU_THRESHOLD" ]; then
        warning "High CPU usage: ${CPU_USAGE}%"
    else
        success "CPU usage: ${CPU_USAGE}%"
    fi
else
    CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}' | cut -d. -f1)
    if [ "$CPU_USAGE" -gt "$CPU_THRESHOLD" ]; then
        warning "High CPU usage: ${CPU_USAGE}%"
    else
        success "CPU usage: ${CPU_USAGE}%"
    fi
fi

# Memory usage
MEMORY_USAGE=$(free | grep Mem | awk '{print int($3/$2 * 100)}')
if [ "$MEMORY_USAGE" -gt "$MEMORY_THRESHOLD" ]; then
    warning "High memory usage: ${MEMORY_USAGE}%"
else
    success "Memory usage: ${MEMORY_USAGE}%"
fi

# Disk usage
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt "$DISK_THRESHOLD" ]; then
    warning "High disk usage: ${DISK_USAGE}%"
else
    success "Disk usage: ${DISK_USAGE}%"
fi

# 5. Check process status
log "Checking process status..."
if command -v systemctl &> /dev/null; then
    if systemctl is-active --quiet ai-test-case-generator; then
        success "Service is running"
        
        # Get process info
        PID=$(systemctl show ai-test-case-generator --property=MainPID --value)
        if [ "$PID" != "0" ]; then
            UPTIME=$(ps -p "$PID" -o etime= | xargs)
            log "Process uptime: $UPTIME"
        fi
    else
        error "Service is not running"
    fi
else
    warning "systemctl not found, skipping service check"
fi

# 6. Check log files for errors
log "Checking recent errors in logs..."
if [ -f "/var/www/ai-test-case-generator/backend/logs/app.log" ]; then
    ERROR_COUNT=$(grep -c "ERROR" /var/www/ai-test-case-generator/backend/logs/app.log 2>/dev/null | tail -100 || echo 0)
    if [ "$ERROR_COUNT" -gt 10 ]; then
        warning "Found $ERROR_COUNT errors in recent logs"
    else
        success "Error count in logs: $ERROR_COUNT"
    fi
fi

# 7. Check disk space for critical directories
log "Checking disk space for critical directories..."
for dir in "/var/www/ai-test-case-generator/backend/uploads" \
           "/var/www/ai-test-case-generator/backend/knowledge_base" \
           "/var/www/ai-test-case-generator/backend/logs"; do
    if [ -d "$dir" ]; then
        DIR_SIZE=$(du -sh "$dir" 2>/dev/null | cut -f1)
        log "Directory size $dir: $DIR_SIZE"
    fi
done

# Summary
echo ""
log "========================================="
log "Health Check Summary"
log "========================================="

if [ $OVERALL_STATUS -eq 0 ]; then
    success "All checks passed!"
else
    error "Some checks failed!"
    echo ""
    log "Issues found:"
    for issue in "${ISSUES[@]}"; do
        echo "  - $issue"
    done
    
    # Send alert
    ALERT_MESSAGE="Health check failed for $APP_NAME:\n$(printf '%s\n' "${ISSUES[@]}")"
    send_alert "$ALERT_MESSAGE"
fi

log "========================================="

exit $OVERALL_STATUS
