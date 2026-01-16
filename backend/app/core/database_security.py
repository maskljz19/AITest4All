"""Database Security Utilities

Provides utilities for secure database operations including:
- Input validation and sanitization
- SQL injection prevention
- Sensitive data encryption
- Audit logging
"""

import logging
import re
from typing import Any, Optional
from datetime import datetime
from sqlalchemy import event
from sqlalchemy.engine import Engine

from app.core.security import APIKeyEncryption

logger = logging.getLogger(__name__)


class DatabaseSecurityValidator:
    """Validator for database input security"""
    
    # Patterns that might indicate SQL injection attempts
    SQL_INJECTION_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b)",
        r"(--|;|\/\*|\*\/)",
        r"(\bOR\b.*=.*)",
        r"(\bAND\b.*=.*)",
        r"('.*--)",
        r"(UNION.*SELECT)",
        r"(xp_.*\()",
    ]
    
    @classmethod
    def validate_input(cls, value: str, field_name: str = "input") -> bool:
        """Validate input for potential SQL injection
        
        Args:
            value: Input value to validate
            field_name: Name of the field (for logging)
            
        Returns:
            True if input is safe, False otherwise
        """
        if not isinstance(value, str):
            return True
        
        # Check for SQL injection patterns
        for pattern in cls.SQL_INJECTION_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                logger.warning(
                    f"Potential SQL injection detected in {field_name}: "
                    f"matched pattern {pattern}"
                )
                return False
        
        return True
    
    @classmethod
    def sanitize_search_query(cls, query: str) -> str:
        """Sanitize search query for full-text search
        
        Args:
            query: Search query string
            
        Returns:
            Sanitized query string
        """
        # Remove special characters that could cause issues
        # Keep only alphanumeric, spaces, and basic punctuation
        sanitized = re.sub(r'[^\w\s\-_.]', ' ', query)
        
        # Remove multiple spaces
        sanitized = re.sub(r'\s+', ' ', sanitized)
        
        # Trim
        sanitized = sanitized.strip()
        
        return sanitized
    
    @classmethod
    def validate_limit_offset(cls, limit: int, offset: int) -> tuple[int, int]:
        """Validate and sanitize limit/offset parameters
        
        Args:
            limit: Query limit
            offset: Query offset
            
        Returns:
            Tuple of (validated_limit, validated_offset)
        """
        # Ensure positive values
        limit = max(1, min(limit, 1000))  # Cap at 1000
        offset = max(0, offset)
        
        return limit, offset


class SensitiveDataEncryption:
    """Utilities for encrypting sensitive data in database"""
    
    SENSITIVE_FIELDS = {
        'api_key', 'secret', 'password', 'token', 'credential'
    }
    
    @classmethod
    def should_encrypt(cls, field_name: str) -> bool:
        """Check if a field should be encrypted
        
        Args:
            field_name: Name of the database field
            
        Returns:
            True if field should be encrypted
        """
        field_lower = field_name.lower()
        return any(sensitive in field_lower for sensitive in cls.SENSITIVE_FIELDS)
    
    @classmethod
    def encrypt_field(cls, value: str) -> str:
        """Encrypt a sensitive field value
        
        Args:
            value: Plain text value
            
        Returns:
            Encrypted value
        """
        if not value:
            return value
        
        try:
            return APIKeyEncryption.encrypt_api_key(value)
        except Exception as e:
            logger.error(f"Failed to encrypt field: {str(e)}")
            raise
    
    @classmethod
    def decrypt_field(cls, value: str) -> str:
        """Decrypt a sensitive field value
        
        Args:
            value: Encrypted value
            
        Returns:
            Plain text value
        """
        if not value:
            return value
        
        try:
            return APIKeyEncryption.decrypt_api_key(value)
        except Exception as e:
            logger.error(f"Failed to decrypt field: {str(e)}")
            raise


class DatabaseAuditLogger:
    """Audit logger for database operations"""
    
    @staticmethod
    def log_query(statement: str, parameters: Optional[dict] = None):
        """Log database query for audit purposes
        
        Args:
            statement: SQL statement
            parameters: Query parameters
        """
        # Only log in development or if audit logging is enabled
        # In production, use a proper audit logging system
        logger.debug(f"DB Query: {statement}")
        if parameters:
            # Mask sensitive parameters
            masked_params = {}
            for key, value in parameters.items():
                if SensitiveDataEncryption.should_encrypt(key):
                    masked_params[key] = "***MASKED***"
                else:
                    masked_params[key] = value
            logger.debug(f"Parameters: {masked_params}")
    
    @staticmethod
    def log_operation(
        operation: str,
        table: str,
        record_id: Optional[int] = None,
        user_id: Optional[str] = None
    ):
        """Log database operation for audit trail
        
        Args:
            operation: Operation type (INSERT, UPDATE, DELETE)
            table: Table name
            record_id: Record ID if applicable
            user_id: User ID if applicable
        """
        logger.info(
            f"DB Operation: {operation} on {table} "
            f"(ID: {record_id}, User: {user_id or 'system'})"
        )


# SQLAlchemy event listeners for security

@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Log queries before execution (for audit purposes)"""
    # Only log in development mode
    if logger.level == logging.DEBUG:
        DatabaseAuditLogger.log_query(statement, parameters)


def setup_database_security():
    """Setup database security measures"""
    logger.info("Database security measures initialized")
    
    # Additional security setup can be added here
    # For example:
    # - Connection encryption
    # - SSL/TLS configuration
    # - Connection pooling limits
    # - Query timeout settings
    
    return True
