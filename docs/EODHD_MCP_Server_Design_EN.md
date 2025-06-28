# EODHD API MCP Server Design Document

## 1. Overview

### 1.1 Purpose
- Build an MCP server to access various EODHD API endpoints
- Provide a unified interface for stock price data, earnings information, and fundamental data

### 1.2 Technology Stack
- **Language**: Python 3.8+
- **MCP Framework**: `mcp` (Model Context Protocol)
- **HTTP Client**: `requests`
- **Data Processing**: `pandas`
- **Environment Variable Management**: `python-dotenv`

## 2. Architecture Design

### 2.1 System Architecture
```
┌─────────────────────────────────────┐
│           MCP Client                │
│        (Claude Code, etc.)          │
└─────────────────┬───────────────────┘
                  │ MCP Protocol
┌─────────────────▼───────────────────┐
│         EODHD MCP Server            │
│  ┌─────────────────────────────────┐ │
│  │        Tools Layer              │ │
│  │  - stock_price                  │ │
│  │  - earnings_calendar            │ │
│  │  - fundamentals                 │ │
│  │  - index_components             │ │
│  └─────────────────────────────────┘ │
│  ┌─────────────────────────────────┐ │
│  │       Service Layer             │ │
│  │  - EODHDApiService              │ │
│  │  - DataProcessor                │ │
│  │  - ErrorHandler                 │ │
│  └─────────────────────────────────┘ │
└─────────────────┬───────────────────┘
                  │ HTTPS
┌─────────────────▼───────────────────┐
│          EODHD API                  │
│    https://eodhd.com/api/           │
└─────────────────────────────────────┘
```

### 2.2 Directory Structure
```
eodhd_mcp_server/
├── README.md
├── requirements.txt
├── setup.py
├── src/
│   └── eodhd_mcp_server/
│       ├── __init__.py
│       ├── server.py           # Main server
│       ├── tools/
│       │   ├── __init__.py
│       │   ├── stock_price.py
│       │   ├── earnings.py
│       │   ├── fundamentals.py
│       │   └── index_components.py
│       ├── services/
│       │   ├── __init__.py
│       │   ├── eodhd_api.py
│       │   ├── data_processor.py
│       │   └── error_handler.py
│       └── utils/
│           ├── __init__.py
│           └── config.py
└── tests/
    ├── __init__.py
    ├── test_tools.py
    └── test_services.py
```

## 3. MCP Tool Definitions

### 3.1 stock_price Tool
```json
{
  "name": "stock_price",
  "description": "Retrieve stock price data (OHLCV)",
  "inputSchema": {
    "type": "object",
    "properties": {
      "symbol": {
        "type": "string",
        "description": "Stock symbol (e.g., AAPL, MSFT)"
      },
      "from_date": {
        "type": "string",
        "description": "Start date (YYYY-MM-DD format)"
      },
      "to_date": {
        "type": "string", 
        "description": "End date (YYYY-MM-DD format)"
      },
      "exchange": {
        "type": "string",
        "description": "Exchange code (default: US)",
        "default": "US"
      }
    },
    "required": ["symbol"]
  }
}
```

### 3.2 earnings_calendar Tool
```json
{
  "name": "earnings_calendar",
  "description": "Retrieve earnings calendar information",
  "inputSchema": {
    "type": "object",
    "properties": {
      "from_date": {
        "type": "string",
        "description": "Start date (YYYY-MM-DD format)"
      },
      "to_date": {
        "type": "string",
        "description": "End date (YYYY-MM-DD format)"
      },
      "symbols": {
        "type": "string",
        "description": "Specific symbols (comma-separated, optional)"
      }
    }
  }
}
```

### 3.3 fundamentals Tool
```json
{
  "name": "fundamentals",
  "description": "Retrieve company fundamental data",
  "inputSchema": {
    "type": "object", 
    "properties": {
      "symbol": {
        "type": "string",
        "description": "Stock symbol"
      },
      "exchange": {
        "type": "string",
        "description": "Exchange code (default: US)",
        "default": "US"
      }
    },
    "required": ["symbol"]
  }
}
```

### 3.4 index_components Tool
```json
{
  "name": "index_components",
  "description": "Retrieve index constituent stocks",
  "inputSchema": {
    "type": "object",
    "properties": {
      "index_code": {
        "type": "string",
        "description": "Index code (e.g., MID.INDX, SML.INDX)"
      }
    },
    "required": ["index_code"]
  }
}
```

## 4. Implementation Specifications

### 4.1 Main Server (server.py)
```python
import asyncio
from mcp.server import Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
from .tools import stock_price, earnings, fundamentals, index_components
from .utils.config import load_config

class EODHDMCPServer:
    def __init__(self):
        self.server = Server("eodhd-mcp-server")
        self.config = load_config()
        self._setup_tools()
    
    def _setup_tools(self):
        # Register tools
        self.server.list_tools = self._list_tools
        self.server.call_tool = self._call_tool
    
    async def _list_tools(self):
        # Return list of available tools
        pass
    
    async def _call_tool(self, name: str, arguments: dict):
        # Execute tools
        pass
```

### 4.2 EODHD API Service (services/eodhd_api.py)
```python
import requests
from typing import Optional, Dict, Any
import pandas as pd
from .error_handler import EODHDErrorHandler

class EODHDApiService:
    BASE_URL = "https://eodhd.com/api"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = self._create_session()
        self.error_handler = EODHDErrorHandler()
    
    def _create_session(self) -> requests.Session:
        """Create session with retry strategy"""
        session = requests.Session()
        # Implement retry configuration
        return session
    
    async def get_eod_data(self, symbol: str, from_date: str = None, 
                          to_date: str = None, exchange: str = "US") -> Dict[str, Any]:
        """Retrieve stock price data"""
        pass
    
    async def get_earnings_calendar(self, from_date: str = None, 
                                  to_date: str = None, symbols: str = None) -> Dict[str, Any]:
        """Retrieve earnings calendar"""
        pass
    
    async def get_fundamentals(self, symbol: str, exchange: str = "US") -> Dict[str, Any]:
        """Retrieve fundamental data"""
        pass
    
    async def get_index_components(self, index_code: str) -> Dict[str, Any]:
        """Retrieve index constituent stocks"""
        pass
```

### 4.3 Data Processor (services/data_processor.py)
```python
import pandas as pd
from typing import Dict, Any, List

class DataProcessor:
    @staticmethod
    def process_eod_data(raw_data: List[Dict]) -> pd.DataFrame:
        """Convert EOD data to DataFrame"""
        pass
    
    @staticmethod
    def process_earnings_data(raw_data: Dict) -> pd.DataFrame:
        """Convert earnings data to DataFrame"""
        pass
    
    @staticmethod
    def process_fundamentals_data(raw_data: Dict) -> Dict[str, Any]:
        """Structure fundamental data"""
        pass
    
    @staticmethod
    def extract_growth_rates(fundamentals: Dict) -> Dict[str, str]:
        """Extract growth rate data"""
        pass
```

### 4.4 Configuration Management (utils/config.py)
```python
import os
from dotenv import load_dotenv
from typing import Dict, Any

def load_config() -> Dict[str, Any]:
    """Load configuration from environment variables"""
    load_dotenv()
    
    config = {
        'api_key': os.getenv('EODHD_API_KEY'),
        'request_timeout': int(os.getenv('REQUEST_TIMEOUT', '30')),
        'max_retries': int(os.getenv('MAX_RETRIES', '3')),
        'rate_limit_delay': float(os.getenv('RATE_LIMIT_DELAY', '0.1'))
    }
    
    if not config['api_key']:
        raise ValueError("EODHD_API_KEY is not set")
    
    return config
```

## 5. Error Handling

### 5.1 Error Classification
- **API Errors**: Rate limits, authentication errors, no data
- **Network Errors**: Timeouts, connection errors
- **Data Errors**: Invalid format, missing data
- **Configuration Errors**: Missing API key, invalid parameters

### 5.2 Error Handler (services/error_handler.py)
```python
import logging
from typing import Optional
import requests

class EODHDErrorHandler:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def handle_api_error(self, response: requests.Response) -> Optional[Exception]:
        """Handle API errors"""
        if response.status_code == 401:
            return ValueError("Invalid API key")
        elif response.status_code == 429:
            return ValueError("API rate limit exceeded")
        elif response.status_code == 404:
            return ValueError("Data not found")
        return None
    
    def handle_network_error(self, error: Exception) -> Exception:
        """Handle network errors"""
        return ConnectionError(f"Network error: {str(error)}")
```

## 6. Security Considerations

### 6.1 API Key Management
- Management via environment variables (`.env` file)
- API key masking in log output
- API key validation functionality

### 6.2 Rate Limiting
- Control API call frequency
- Automatic retry functionality
- Appropriate wait times on errors

## 7. Testing Strategy

### 7.1 Unit Testing
- Functional testing for each tool
- Mock testing for API services
- Data processor testing

### 7.2 Integration Testing
- Integration testing with actual EODHD API
- MCP protocol testing

## 8. Deployment

### 8.1 Packaging
```python
# setup.py
from setuptools import setup, find_packages

setup(
    name="eodhd-mcp-server",
    version="1.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "mcp>=1.0.0",
        "requests>=2.31.0", 
        "pandas>=2.0.0",
        "python-dotenv>=1.0.0"
    ],
    entry_points={
        "console_scripts": [
            "eodhd-mcp-server=eodhd_mcp_server.server:main"
        ]
    }
)
```

### 8.2 Installation Instructions
```bash
# Development environment execution
cd eodhd_mcp_server
pip install -e .

# Production environment execution
pip install eodhd-mcp-server
```

## 9. Usage Examples

### 9.1 Using with MCP Client
```python
# Usage example from Claude Code
tools = mcp_client.list_tools()
result = mcp_client.call_tool("stock_price", {
    "symbol": "AAPL",
    "from_date": "2024-01-01",
    "to_date": "2024-12-31"
})
```

## 10. Performance Considerations

### 10.1 Caching Strategy
- Implement response caching for frequently requested data
- Cache invalidation based on data freshness requirements
- Memory-efficient caching mechanisms

### 10.2 Optimization
- Batch processing for multiple symbol requests
- Asynchronous API calls for improved throughput
- Connection pooling for HTTP requests

## 11. Monitoring and Logging

### 11.1 Logging Strategy
- Structured logging with appropriate log levels
- Request/response logging for debugging
- Performance metrics logging

### 11.2 Health Checks
- API connectivity monitoring
- Service health endpoints
- Error rate tracking

## 12. Future Enhancements

### 12.1 Additional Data Sources
- Support for additional financial data providers
- Real-time data streaming capabilities
- Alternative data sources integration

### 12.2 Advanced Features
- Data aggregation and analytics tools
- Custom alert systems
- Portfolio management tools 