"""Custom exceptions for EODHD MCP Server."""


class EODHDError(Exception):
    """Base exception for EODHD MCP Server."""
    pass


class APIError(EODHDError):
    """Exception raised for API-related errors."""
    
    def __init__(self, message: str, status_code: int = None, response_data: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class AuthenticationError(APIError):
    """Exception raised for authentication errors."""
    pass


class RateLimitError(APIError):
    """Exception raised when API rate limit is exceeded."""
    pass


class DataNotFoundError(APIError):
    """Exception raised when requested data is not found."""
    pass


class NetworkError(EODHDError):
    """Exception raised for network-related errors."""
    pass


class ConfigurationError(EODHDError):
    """Exception raised for configuration errors."""
    pass


class DataProcessingError(EODHDError):
    """Exception raised for data processing errors."""
    pass