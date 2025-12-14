"""
Custom exception classes for application-specific errors.
"""


class DatabaseError(Exception):
    """Raised when database operations fail."""
    pass


class ValidationError(Exception):
    """Raised when data validation fails."""
    pass


class S3Error(Exception):
    """Raised when S3 operations fail."""
    pass


class VibeAPIError(Exception):
    """Raised when Vibe API calls fail."""
    pass


class ETLError(Exception):
    """Raised when ETL pipeline encounters errors."""
    pass


class AuthenticationError(Exception):
    """Raised when authentication fails."""
    pass


class AuthorizationError(Exception):
    """Raised when user lacks permissions."""
    pass


class FileUploadError(Exception):
    """Raised when file upload processing fails."""
    pass


class ConfigurationError(Exception):
    """Raised when configuration is invalid."""
    pass
