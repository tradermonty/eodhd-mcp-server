"""Tests for configuration module."""

import pytest
import os
from unittest.mock import patch

from eodhd_mcp_server.config import Config


class TestConfig:
    """Test class for Config."""
    
    @patch.dict(os.environ, {
        'EODHD_API_KEY': 'test_api_key',
        'EODHD_BASE_URL': 'https://test.com/api',
        'REQUEST_TIMEOUT': '60',
        'MAX_RETRIES': '5',
        'RATE_LIMIT_DELAY': '0.5',
        'DEBUG': 'true'
    })
    def test_config_with_env_vars(self):
        """Test configuration loading with environment variables."""
        config = Config()
        
        assert config.api_key == 'test_api_key'
        assert config.base_url == 'https://test.com/api'
        assert config.request_timeout == 60
        assert config.max_retries == 5
        assert config.rate_limit_delay == 0.5
        assert config.debug is True
    
    @patch.dict(os.environ, {}, clear=True)
    def test_config_missing_api_key(self):
        """Test configuration fails when API key is missing."""
        with pytest.raises(ValueError, match="EODHD_API_KEY environment variable is required"):
            Config()
    
    @patch.dict(os.environ, {
        'EODHD_API_KEY': 'test_key'
    })
    def test_config_with_defaults(self):
        """Test configuration with default values."""
        config = Config()
        
        assert config.api_key == 'test_key'
        assert config.base_url == 'https://eodhd.com/api'
        assert config.request_timeout == 30
        assert config.max_retries == 3
        assert config.rate_limit_delay == 0.1
        assert config.debug is False
    
    @patch.dict(os.environ, {
        'EODHD_API_KEY': 'test_key',
        'DEBUG': 'false'
    })
    def test_debug_false(self):
        """Test debug flag with false value."""
        config = Config()
        assert config.debug is False
    
    @patch.dict(os.environ, {
        'EODHD_API_KEY': 'test_key',
        'DEBUG': 'TRUE'
    })
    def test_debug_case_insensitive(self):
        """Test debug flag is case insensitive."""
        config = Config()
        assert config.debug is True
    
    @patch.dict(os.environ, {
        'EODHD_API_KEY': 'test_key'
    })
    def test_get_method(self):
        """Test the get method."""
        config = Config()
        
        assert config.get('api_key') == 'test_key'
        assert config.get('nonexistent_key') is None
        assert config.get('nonexistent_key', 'default') == 'default'