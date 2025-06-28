"""EODHD API client for making HTTP requests."""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

import httpx
import pandas as pd

from .config import config
from .exceptions import (
    APIError,
    AuthenticationError,
    RateLimitError,
    DataNotFoundError,
    NetworkError,
    DataProcessingError
)


logger = logging.getLogger(__name__)


class EODHDClient:
    """Client for interacting with EODHD API."""
    
    def __init__(self):
        """Initialize the EODHD API client."""
        self.base_url = config.base_url
        self.api_key = config.api_key
        self.timeout = config.request_timeout
        self.max_retries = config.max_retries
        self.rate_limit_delay = config.rate_limit_delay
        
        # Create HTTP client with retry configuration
        self.client = httpx.AsyncClient(
            timeout=self.timeout,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
        )
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.client.aclose()
    
    def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """Handle HTTP response and raise appropriate exceptions."""
        if response.status_code == 401:
            raise AuthenticationError("Invalid API key", response.status_code)
        elif response.status_code == 429:
            raise RateLimitError("API rate limit exceeded", response.status_code)
        elif response.status_code == 404:
            raise DataNotFoundError("Data not found", response.status_code)
        elif response.status_code >= 400:
            raise APIError(f"API error: {response.status_code}", response.status_code)
        
        try:
            return response.json()
        except ValueError as e:
            raise DataProcessingError(f"Failed to parse JSON response: {e}")
    
    async def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make HTTP request with retry logic."""
        url = f"{self.base_url}/{endpoint}"
        params['api_token'] = self.api_key
        
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"Making request to {url} with params: {params}")
                response = await self.client.get(url, params=params)
                
                if response.status_code == 429 and attempt < self.max_retries - 1:
                    # Rate limited, wait and retry
                    await asyncio.sleep(self.rate_limit_delay * (2 ** attempt))
                    continue
                
                return self._handle_response(response)
                
            except httpx.RequestError as e:
                if attempt == self.max_retries - 1:
                    raise NetworkError(f"Network error after {self.max_retries} attempts: {e}")
                await asyncio.sleep(self.rate_limit_delay * (2 ** attempt))
        
        raise NetworkError(f"Failed to make request after {self.max_retries} attempts")
    
    async def get_eod_data(
        self,
        symbol: str,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        exchange: str = "US"
    ) -> List[Dict[str, Any]]:
        """
        Get End-of-Day stock price data.
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            from_date: Start date in YYYY-MM-DD format
            to_date: End date in YYYY-MM-DD format
            exchange: Exchange code (default: 'US')
            
        Returns:
            List of OHLCV data dictionaries
        """
        endpoint = f"eod/{symbol}.{exchange}"
        params = {}
        
        if from_date:
            params['from'] = from_date
        if to_date:
            params['to'] = to_date
        
        params['fmt'] = 'json'
        
        response = await self._make_request(endpoint, params)
        
        # Ensure response is a list
        if isinstance(response, dict):
            return [response]
        return response
    
    async def get_earnings_calendar(
        self,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        symbols: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get earnings calendar data.
        
        Args:
            from_date: Start date in YYYY-MM-DD format
            to_date: End date in YYYY-MM-DD format
            symbols: Comma-separated list of symbols (optional)
            
        Returns:
            List of earnings calendar data dictionaries
        """
        endpoint = "calendar/earnings"
        params = {}
        
        if from_date:
            params['from'] = from_date
        if to_date:
            params['to'] = to_date
        if symbols:
            params['symbols'] = symbols
        
        params['fmt'] = 'json'
        
        response = await self._make_request(endpoint, params)
        
        # Handle different response formats
        if isinstance(response, dict):
            # If response is a dict with 'earnings' key
            if 'earnings' in response:
                return response['earnings']
            # If response is a dict representing a single earning
            return [response]
        return response
    
    async def get_fundamentals(
        self,
        symbol: str,
        exchange: str = "US"
    ) -> Dict[str, Any]:
        """
        Get fundamental data for a company.
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            exchange: Exchange code (default: 'US')
            
        Returns:
            Dictionary containing fundamental data
        """
        endpoint = f"fundamentals/{symbol}.{exchange}"
        params = {'fmt': 'json'}
        
        response = await self._make_request(endpoint, params)
        return response
    
    async def get_index_components(
        self,
        index_code: str
    ) -> List[Dict[str, Any]]:
        """
        Get index components data.
        
        Args:
            index_code: Index code (e.g., 'MID.INDX', 'SML.INDX')
            
        Returns:
            List of index component data dictionaries
        """
        endpoint = f"fundamentals/{index_code}"
        params = {'fmt': 'json'}
        
        response = await self._make_request(endpoint, params)
        
        # Extract components from response
        if isinstance(response, dict):
            # Look for components in various possible keys
            for key in ['Components', 'components', 'Holdings', 'holdings']:
                if key in response:
                    components = response[key]
                    if isinstance(components, dict):
                        # Convert dict to list of dicts
                        return [{'symbol': k, **v} for k, v in components.items()]
                    return components
            
            # If no components found, return the response as a single item
            return [response]
        
        return response