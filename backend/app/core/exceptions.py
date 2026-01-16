"""Custom Exception Classes"""

from typing import Optional, Dict, Any


class AppException(Exception):
    """Base exception for application errors"""
    
    def __init__(
        self,
        message: str,
        error_code: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class LLMAPIError(AppException):
    """Exception raised when LLM API call fails"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="LLM_API_ERROR",
            status_code=503,
            details=details
        )


class DocumentParseError(AppException):
    """Exception raised when document parsing fails"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="DOCUMENT_PARSE_ERROR",
            status_code=400,
            details=details
        )


class ScriptExecutionError(AppException):
    """Exception raised when script execution fails"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="SCRIPT_EXECUTION_ERROR",
            status_code=500,
            details=details
        )


class KnowledgeBaseError(AppException):
    """Exception raised for knowledge base operations"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="KB_SEARCH_ERROR",
            status_code=500,
            details=details
        )


class SessionError(AppException):
    """Exception raised for session operations"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="SESSION_ERROR",
            status_code=400,
            details=details
        )


class SessionExpiredError(AppException):
    """Exception raised when session has expired"""
    
    def __init__(self, message: str = "Session has expired", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="SESSION_EXPIRED",
            status_code=410,
            details=details
        )


class ValidationError(AppException):
    """Exception raised for validation errors"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=400,
            details=details
        )


class ResourceNotFoundError(AppException):
    """Exception raised when resource is not found"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="RESOURCE_NOT_FOUND",
            status_code=404,
            details=details
        )


class TimeoutError(AppException):
    """Exception raised when operation times out"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="TIMEOUT_ERROR",
            status_code=408,
            details=details
        )


class FileSizeExceededError(AppException):
    """Exception raised when file size exceeds limit"""
    
    def __init__(self, message: str = "File size exceeds 10MB limit", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="FILE_SIZE_EXCEEDED",
            status_code=413,
            details=details
        )


class UnsupportedFileTypeError(AppException):
    """Exception raised when file type is not supported"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="UNSUPPORTED_FILE_TYPE",
            status_code=415,
            details=details
        )
