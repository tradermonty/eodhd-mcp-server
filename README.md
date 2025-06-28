# EODHD MCP Server

*Language: English | [日本語](README_JA.md)*

A Model Context Protocol (MCP) server that provides access to EODHD financial APIs. This server enables Claude Code and other MCP clients to fetch stock prices, earnings data, fundamental information, and index components through a unified interface.

## Features

- **Stock Price Data**: Get historical End-of-Day (EOD) OHLCV data
- **Earnings Calendar**: Access earnings announcement schedules and estimates
- **Fundamental Data**: Retrieve comprehensive company financial metrics
- **Index Components**: Get constituent information for market indices
- **Growth Metrics**: Extract and analyze growth rate data

## Available Tools

### 1. `get_stock_price`
Retrieve End-of-Day stock price data for any symbol.

**Parameters:**
- `symbol` (required): Stock symbol (e.g., 'AAPL', 'MSFT')
- `from_date` (optional): Start date in YYYY-MM-DD format
- `to_date` (optional): End date in YYYY-MM-DD format  
- `exchange` (optional): Exchange code (default: 'US')

### 2. `get_earnings_calendar`
Get earnings calendar information for specified date ranges and symbols.

**Parameters:**
- `from_date` (optional): Start date in YYYY-MM-DD format
- `to_date` (optional): End date in YYYY-MM-DD format
- `symbols` (optional): Comma-separated list of symbols

### 3. `get_fundamentals`
Access comprehensive fundamental data for companies.

**Parameters:**
- `symbol` (required): Stock symbol
- `exchange` (optional): Exchange code (default: 'US')

### 4. `get_index_components`
Retrieve constituent information for market indices.

**Parameters:**
- `index_code` (required): Index code (e.g., 'MID.INDX', 'SML.INDX')

### 5. `get_growth_rates`
Extract growth rate metrics from fundamental data.

**Parameters:**
- `symbol` (required): Stock symbol
- `exchange` (optional): Exchange code (default: 'US')

## Installation

### Prerequisites
- Python 3.8 or higher
- EODHD API key (sign up at [eodhd.com](https://eodhd.com))

### Setup

1. **Clone and setup the project:**
```bash
# Clone the repository
git clone <repository-url>
cd eodhd-mcp-server

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
venv\\Scripts\\activate     # On Windows

# Install dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

2. **Configure environment variables:**
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env file and add your EODHD API key
EODHD_API_KEY=your_actual_api_key_here
```

3. **Test the installation:**
```bash
# Test if the server starts correctly (press Ctrl+C to stop)
eodhd-mcp-server

# You should see output similar to:
# 2024-06-28 16:04:42,657 - eodhd_mcp_server.server - INFO - Starting EODHD MCP Server...
# 2024-06-28 16:04:42,657 - eodhd_mcp_server.server - INFO - Configuration loaded - API key configured: True
```

## Usage

### Running the MCP Server

The server runs as a stdio-based MCP server:

```bash
eodhd-mcp-server
```

### Integration with Cursor

Add the server to your Cursor MCP configuration (`~/.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "eodhd": {
      "command": "/path/to/your/project/venv/bin/eodhd-mcp-server",
      "args": [],
      "cwd": "/path/to/your/project/eodhd-mcp-server",
      "env": {
        "EODHD_API_KEY": "your_api_key_here",
        "EODHD_BASE_URL": "https://eodhd.com/api",
        "REQUEST_TIMEOUT": "30",
        "MAX_RETRIES": "3",
        "RATE_LIMIT_DELAY": "0.1",
        "DEBUG": "false"
      }
    }
  }
}
```

**Important Configuration Notes:**
- Replace `/path/to/your/project/` with your actual project path
- Use the absolute path to the `eodhd-mcp-server` executable in your virtual environment
- Set the `cwd` (current working directory) to your project root
- Include all necessary environment variables in the `env` section
- Replace `your_api_key_here` with your actual EODHD API key

**Alternative: Using .env file**
If you prefer to use a `.env` file (recommended for security), you can simplify the configuration:

```json
{
  "mcpServers": {
    "eodhd": {
      "command": "/path/to/your/project/venv/bin/eodhd-mcp-server",
      "args": [],
      "cwd": "/path/to/your/project/eodhd-mcp-server"
    }
  }
}
```

Make sure your `.env` file contains all required environment variables.

### Example Usage in Cursor

Once the MCP server is configured and running (green icon), you can use the tools in Cursor:

**Stock Price Data:**
- "Get AAPL stock price for the last 30 days"
- "Show me Tesla's stock performance this year"

**Earnings Information:**
- "Show me earnings announcements for this week"
- "Get AAPL's past 10 earnings results"

**Fundamental Analysis:**
- "Get Microsoft's fundamental data"
- "Show me growth rates for NVDA"

**Index Components:**
- "What are the components of the S&P 500?"
- "Show me the Russell 2000 holdings"

The server will automatically handle the API calls and return formatted, readable results.

## Configuration

### Environment Variables

- `EODHD_API_KEY`: Your EODHD API key (required)
- `EODHD_BASE_URL`: Base URL for EODHD API (default: https://eodhd.com/api)
- `REQUEST_TIMEOUT`: Request timeout in seconds (default: 30)
- `MAX_RETRIES`: Maximum retry attempts (default: 3)
- `RATE_LIMIT_DELAY`: Delay between requests in seconds (default: 0.1)
- `DEBUG`: Enable debug logging (default: false)

### API Key

Get your free API key from [EODHD](https://eodhd.com/):
1. Sign up for an account
2. Navigate to the API section
3. Copy your API key
4. Add it to your `.env` file

## Error Handling

The server includes comprehensive error handling for:

- **API Errors**: Invalid API keys, rate limits, data not found
- **Network Errors**: Connection timeouts, network failures
- **Data Processing Errors**: Invalid data formats, parsing failures
- **Configuration Errors**: Missing API keys, invalid parameters

## Development

### Project Structure

```
eodhd-mcp-server/
├── src/eodhd_mcp_server/
│   ├── __init__.py          # Package initialization
│   ├── server.py            # Main MCP server with tools
│   ├── api_client.py        # EODHD API client
│   ├── data_processor.py    # Data processing utilities
│   ├── config.py            # Configuration management
│   └── exceptions.py        # Custom exceptions
├── tests/                   # Test files (to be implemented)
├── requirements.txt         # Python dependencies
├── pyproject.toml          # Package configuration
├── .env.example            # Example environment file
└── README.md               # This file
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## API Compatibility

This server maintains compatibility with existing stocktrading codebase by:

- Preserving DataFrame structures used in existing code
- Maintaining consistent column names and data types
- Supporting the same API response formats
- Following established error handling patterns

## License

MIT License - see LICENSE file for details.

## Troubleshooting

### Red Icon in Cursor (Server Not Working)

If you see a red icon next to the EODHD MCP server in Cursor:

1. **Check Configuration Path**: Ensure the `command` path points to the correct location:
   ```bash
   # Find the correct path
   source venv/bin/activate
   which eodhd-mcp-server
   ```

2. **Verify Environment Variables**: Make sure your `.env` file exists and contains:
   ```
   EODHD_API_KEY=your_actual_api_key
   ```

3. **Test Server Manually**: Try running the server directly:
   ```bash
   source venv/bin/activate
   eodhd-mcp-server
   ```

4. **Check Cursor Configuration**: Ensure your `~/.cursor/mcp.json` includes:
   - Absolute path to the executable
   - Correct working directory (`cwd`)
   - Environment variables or `.env` file access

5. **Restart Cursor**: After configuration changes, completely restart Cursor.

### Common Issues

- **API Key Issues**: Verify your EODHD API key is valid and has sufficient quota
- **Path Issues**: Use absolute paths in Cursor configuration
- **Permission Issues**: Ensure the executable has proper permissions
- **Virtual Environment**: Make sure you're using the correct virtual environment path

## Support

For issues and questions:
1. Check the [EODHD API documentation](https://eodhd.com/financial-api/)
2. Review error messages in debug mode (`DEBUG=true`)
3. Use the troubleshooting guide above
4. Open an issue in the repository

## Changelog

### Version 1.0.0
- Initial release
- Support for stock prices, earnings calendar, fundamentals, and index components
- Comprehensive error handling and data processing
- MCP protocol integration with FastMCP