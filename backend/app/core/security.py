"""Security utilities for file upload and validation"""

import os
import re
import hashlib
from pathlib import Path
from typing import Optional, Tuple
from fastapi import UploadFile, HTTPException
import logging
import base64

# Optional import for encryption
try:
    from cryptography.fernet import Fernet
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False
    logging.warning("cryptography not available. API key encryption will be disabled.")

# Optional import for file type detection
try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False
    logging.warning("python-magic not available. File type detection will be limited.")

from app.core.config import settings

logger = logging.getLogger(__name__)


class APIKeyEncryption:
    """Encryption utilities for API keys"""
    
    @staticmethod
    def _get_encryption_key() -> bytes:
        """Get or generate encryption key
        
        Returns:
            Encryption key bytes
        """
        if not CRYPTOGRAPHY_AVAILABLE:
            raise RuntimeError("cryptography library not available. Install with: pip install cryptography")
        
        # Try to get key from environment
        key_str = os.getenv('ENCRYPTION_KEY')
        
        if not key_str:
            # Generate a new key (should be stored securely in production)
            key = Fernet.generate_key()
            logger.warning("No ENCRYPTION_KEY found in environment. Generated new key. "
                         "Please set ENCRYPTION_KEY in .env for production use.")
            return key
        
        # Decode base64 key
        try:
            return base64.urlsafe_b64decode(key_str)
        except Exception as e:
            logger.error(f"Failed to decode encryption key: {str(e)}")
            raise ValueError("Invalid encryption key format")
    
    @classmethod
    def encrypt_api_key(cls, api_key: str) -> str:
        """Encrypt an API key
        
        Args:
            api_key: Plain text API key
            
        Returns:
            Encrypted API key (base64 encoded)
        """
        if not api_key:
            return ""
        
        if not CRYPTOGRAPHY_AVAILABLE:
            logger.warning("Cryptography not available, returning unencrypted key")
            return api_key
        
        try:
            key = cls._get_encryption_key()
            f = Fernet(key)
            encrypted = f.encrypt(api_key.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            logger.error(f"Failed to encrypt API key: {str(e)}")
            raise ValueError("Failed to encrypt API key")
    
    @classmethod
    def decrypt_api_key(cls, encrypted_key: str) -> str:
        """Decrypt an API key
        
        Args:
            encrypted_key: Encrypted API key (base64 encoded)
            
        Returns:
            Plain text API key
        """
        if not encrypted_key:
            return ""
        
        if not CRYPTOGRAPHY_AVAILABLE:
            logger.warning("Cryptography not available, returning key as-is")
            return encrypted_key
        
        try:
            key = cls._get_encryption_key()
            f = Fernet(key)
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_key)
            decrypted = f.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Failed to decrypt API key: {str(e)}")
            raise ValueError("Failed to decrypt API key")
    
    @classmethod
    def mask_api_key(cls, api_key: str, visible_chars: int = 4) -> str:
        """Mask an API key for display
        
        Args:
            api_key: Plain text API key
            visible_chars: Number of characters to show at the end
            
        Returns:
            Masked API key (e.g., "sk-...xyz123")
        """
        if not api_key or len(api_key) <= visible_chars:
            return "***"
        
        return f"{api_key[:3]}...{api_key[-visible_chars:]}"


class FileSecurityValidator:
    """Validator for file upload security"""
    
    # Allowed file extensions and their MIME types
    ALLOWED_EXTENSIONS = {
        '.docx': ['application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
        '.pdf': ['application/pdf'],
        '.md': ['text/markdown', 'text/plain'],
        '.xlsx': ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'],
        '.txt': ['text/plain'],
    }
    
    # Maximum file size in bytes (10MB by default)
    MAX_FILE_SIZE = settings.max_upload_size_mb * 1024 * 1024
    
    # Dangerous filename patterns
    DANGEROUS_PATTERNS = [
        r'\.\.',  # Path traversal
        r'[<>:"|?*]',  # Invalid Windows characters
        r'^\.', # Hidden files
        r'[\x00-\x1f]',  # Control characters
    ]
    
    @classmethod
    def validate_filename(cls, filename: str) -> Tuple[bool, Optional[str]]:
        """Validate filename for security issues
        
        Args:
            filename: Original filename
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not filename:
            return False, "Filename cannot be empty"
        
        # Check for dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, filename):
                return False, f"Filename contains dangerous pattern: {pattern}"
        
        # Check filename length
        if len(filename) > 255:
            return False, "Filename too long (max 255 characters)"
        
        # Check file extension
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext not in cls.ALLOWED_EXTENSIONS:
            return False, f"File extension not allowed. Allowed: {', '.join(cls.ALLOWED_EXTENSIONS.keys())}"
        
        return True, None
    
    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        """Sanitize filename by removing dangerous characters
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        # Get base name and extension
        name, ext = os.path.splitext(filename)
        
        # Remove dangerous characters
        name = re.sub(r'[^\w\s-]', '', name)
        name = re.sub(r'[-\s]+', '-', name)
        name = name.strip('-')
        
        # Limit length
        if len(name) > 200:
            name = name[:200]
        
        # Add timestamp hash to avoid collisions
        timestamp_hash = hashlib.md5(str(os.urandom(16)).encode()).hexdigest()[:8]
        
        return f"{name}_{timestamp_hash}{ext.lower()}"
    
    @classmethod
    async def validate_file_size(cls, file: UploadFile) -> Tuple[bool, Optional[str]]:
        """Validate file size
        
        Args:
            file: Uploaded file
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Read file to check size
        content = await file.read()
        file_size = len(content)
        
        # Reset file pointer
        await file.seek(0)
        
        if file_size > cls.MAX_FILE_SIZE:
            max_mb = cls.MAX_FILE_SIZE / (1024 * 1024)
            return False, f"File size exceeds maximum allowed size of {max_mb}MB"
        
        if file_size == 0:
            return False, "File is empty"
        
        return True, None
    
    @classmethod
    async def validate_file_type(cls, file: UploadFile) -> Tuple[bool, Optional[str]]:
        """Validate file type using magic numbers (file signature)
        
        Args:
            file: Uploaded file
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Get file extension
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in cls.ALLOWED_EXTENSIONS:
            return False, f"File extension not allowed: {file_ext}"
        
        # If python-magic is not available, skip MIME type detection
        if not MAGIC_AVAILABLE:
            logger.warning("python-magic not available, skipping MIME type validation")
            return True, None
        
        # Read first 2048 bytes for magic number detection
        content = await file.read(2048)
        await file.seek(0)
        
        try:
            # Detect MIME type using python-magic
            mime_type = magic.from_buffer(content, mime=True)
            
            # Check if detected MIME type matches allowed types for this extension
            allowed_mimes = cls.ALLOWED_EXTENSIONS[file_ext]
            
            if mime_type not in allowed_mimes:
                # Special case: text/plain is acceptable for .md files
                if file_ext == '.md' and mime_type == 'text/plain':
                    return True, None
                
                logger.warning(f"MIME type mismatch: expected {allowed_mimes}, got {mime_type}")
                return False, f"File type mismatch: file appears to be {mime_type}, not {file_ext}"
            
            return True, None
            
        except Exception as e:
            logger.error(f"Failed to detect file type: {str(e)}")
            # If magic detection fails, fall back to extension check only
            return True, None
    
    @classmethod
    async def validate_upload(cls, file: UploadFile) -> Tuple[bool, Optional[str], Optional[str]]:
        """Comprehensive file upload validation
        
        Args:
            file: Uploaded file
            
        Returns:
            Tuple of (is_valid, error_message, sanitized_filename)
        """
        # Validate filename
        is_valid, error = cls.validate_filename(file.filename)
        if not is_valid:
            return False, error, None
        
        # Validate file size
        is_valid, error = await cls.validate_file_size(file)
        if not is_valid:
            return False, error, None
        
        # Validate file type
        is_valid, error = await cls.validate_file_type(file)
        if not is_valid:
            return False, error, None
        
        # Sanitize filename
        sanitized_name = cls.sanitize_filename(file.filename)
        
        return True, None, sanitized_name


async def validate_and_save_upload(
    file: UploadFile,
    upload_dir: str,
    allowed_extensions: Optional[list] = None
) -> Tuple[str, str]:
    """Validate and save uploaded file securely
    
    Args:
        file: Uploaded file
        upload_dir: Directory to save file
        allowed_extensions: Optional list of allowed extensions (overrides default)
        
    Returns:
        Tuple of (file_path, sanitized_filename)
        
    Raises:
        HTTPException: If validation fails
    """
    # Validate upload
    is_valid, error, sanitized_name = await FileSecurityValidator.validate_upload(file)
    
    if not is_valid:
        raise HTTPException(status_code=400, detail=error)
    
    # Create upload directory if it doesn't exist
    upload_path = Path(upload_dir)
    upload_path.mkdir(parents=True, exist_ok=True)
    
    # Save file
    file_path = upload_path / sanitized_name
    
    try:
        content = await file.read()
        with open(file_path, 'wb') as f:
            f.write(content)
        
        logger.info(f"File saved successfully: {file_path}")
        return str(file_path), sanitized_name
        
    except Exception as e:
        logger.error(f"Failed to save file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")


def validate_path_traversal(file_path: str, base_dir: str) -> bool:
    """Validate that file_path doesn't escape base_dir
    
    Args:
        file_path: File path to validate
        base_dir: Base directory that should contain the file
        
    Returns:
        True if path is safe, False otherwise
    """
    try:
        # Resolve absolute paths
        abs_file_path = Path(file_path).resolve()
        abs_base_dir = Path(base_dir).resolve()
        
        # Check if file path is within base directory
        return abs_file_path.is_relative_to(abs_base_dir)
        
    except Exception as e:
        logger.error(f"Path validation error: {str(e)}")
        return False
