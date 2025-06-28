"""Configuration management for EODHD MCP Server."""

import os
from dotenv import load_dotenv
from typing import Dict, Any


class Config:
    """Configuration class for EODHD MCP Server."""
    
    def __init__(self):
        """Initialize configuration by loading environment variables."""
        load_dotenv()
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from environment variables."""
        config = {
            'api_key': os.getenv('EODHD_API_KEY'),
            'base_url': os.getenv('EODHD_BASE_URL', 'https://eodhd.com/api'),
            'request_timeout': int(os.getenv('REQUEST_TIMEOUT', '30')),
            'max_retries': int(os.getenv('MAX_RETRIES', '3')),
            'rate_limit_delay': float(os.getenv('RATE_LIMIT_DELAY', '0.1')),
            'debug': os.getenv('DEBUG', 'false').lower() == 'true'
        }
        
        if not config['api_key']:
            raise ValueError(
                "EODHD_API_KEY environment variable is required. "
                "Please set it in your .env file or environment."
            )
        
        return config
    
    def get(self, key: str, default=None):
        """Get configuration value by key."""
        return self._config.get(key, default)
    
    @property
    def api_key(self) -> str:
        """Get EODHD API key."""
        return self._config['api_key']
    
    @property
    def base_url(self) -> str:
        """Get EODHD base URL."""
        return self._config['base_url']
    
    @property
    def request_timeout(self) -> int:
        """Get request timeout in seconds."""
        return self._config['request_timeout']
    
    @property
    def max_retries(self) -> int:
        """Get maximum number of retries."""
        return self._config['max_retries']
    
    @property
    def rate_limit_delay(self) -> float:
        """Get rate limit delay in seconds."""
        return self._config['rate_limit_delay']
    
    @property
    def debug(self) -> bool:
        """Get debug flag."""
        return self._config['debug']


# Global configuration instance
config = Config()