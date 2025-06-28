# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an **EODHD MCP Server** project designed to provide access to EODHD financial APIs through the Model Context Protocol (MCP). The project creates a server that exposes stock price data, earnings calendar, fundamentals, and index components data from EODHD APIs as MCP tools.

## Development Environment

### Virtual Environment Setup
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Deactivate when done
deactivate
```

### Dependencies Installation
The project uses Python 3.8+ with the following key dependencies (as defined in the design document):
- `mcp` - Model Context Protocol framework
- `requests` - HTTP client for API calls
- `pandas` - Data processing and manipulation
- `python-dotenv` - Environment variable management

Install dependencies:
```bash
pip install -r requirements.txt
# or for development installation:
pip install -e .
```

## Project Architecture

### High-Level Structure
Based on the design document, the project follows this architecture:

```
eodhd_mcp_server/
├── src/
│   └── eodhd_mcp_server/
│       ├── server.py           # Main MCP server
│       ├── tools/              # MCP tool implementations
│       │   ├── stock_price.py
│       │   ├── earnings.py
│       │   ├── fundamentals.py
│       │   └── index_components.py
│       ├── services/           # Business logic layer
│       │   ├── eodhd_api.py    # EODHD API client
│       │   ├── data_processor.py
│       │   └── error_handler.py
│       └── utils/
│           └── config.py       # Configuration management
└── tests/                      # Test files
```

### Key Components

1. **MCP Tools Layer**: Exposes four main tools:
   - `stock_price` - Retrieves OHLCV stock price data
   - `earnings_calendar` - Gets earnings calendar information
   - `fundamentals` - Fetches company fundamental data
   - `index_components` - Returns index constituent information

2. **Service Layer**: 
   - `EODHDApiService` - Handles HTTP requests to EODHD APIs
   - `DataProcessor` - Processes and formats API responses
   - `ErrorHandler` - Manages API errors and network issues

3. **Configuration**: Environment-based configuration using `.env` file for API keys and settings

## Environment Configuration

### Required Environment Variables
Create a `.env` file in the project root:
```bash
EODHD_API_KEY=your_api_key_here
REQUEST_TIMEOUT=30
MAX_RETRIES=3
RATE_LIMIT_DELAY=0.1
```

### API Key Security
- Never commit API keys to version control
- Store keys in `.env` file (add to `.gitignore`)
- Use environment variables in production

## MCP Integration

### Server Execution
The MCP server is designed to be executed as:
```bash
eodhd-mcp-server
```

### Tool Interface
Each tool follows MCP protocol standards with defined input schemas for parameters like:
- Stock symbols (e.g., "AAPL", "MSFT")
- Date ranges (YYYY-MM-DD format)
- Exchange codes (default: "US")

## Data Integration Notes

### EODHD API Endpoints Mapping
- Stock prices: `/api/eod/{symbol}.US`
- Earnings calendar: `/api/calendar/earnings`
- Fundamentals: `/api/fundamentals/{symbol}.US`
- Index components: `/api/fundamentals/{index}.INDX`

### Data Format Compatibility
The server maintains compatibility with existing stocktrading codebase by:
- Preserving DataFrame structures used in existing code
- Maintaining consistent column names and data types
- Supporting the same API response formats

## Error Handling

The system handles multiple error types:
- **API Errors**: Rate limits (429), authentication (401), data not found (404)
- **Network Errors**: Timeouts, connection failures
- **Data Errors**: Invalid formats, missing data
- **Configuration Errors**: Missing API keys, invalid parameters

## Testing

### Test Structure
- Unit tests for individual tools and services
- Integration tests with EODHD API (using test keys)
- MCP protocol compliance tests

### Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_tools.py

# Run with coverage
pytest --cov=src/eodhd_mcp_server
```

## Development Workflow

1. **Setup**: Create virtual environment and install dependencies
2. **Configuration**: Set up `.env` file with API credentials
3. **Development**: Implement features following the layered architecture
4. **Testing**: Run tests before committing changes
5. **Integration**: Test MCP protocol integration with clients

## Key Development Principles

- **Layered Architecture**: Separate concerns between tools, services, and utilities
- **Error Resilience**: Implement comprehensive error handling and retries
- **Rate Limiting**: Respect EODHD API rate limits with delays and backoff
- **Data Consistency**: Maintain compatibility with existing data formats
- **Security**: Never expose API keys in logs or commits