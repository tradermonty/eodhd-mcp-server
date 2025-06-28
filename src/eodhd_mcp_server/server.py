"""EODHD MCP Server - Main server implementation using FastMCP."""

import asyncio
import logging
from typing import Optional, List
from datetime import datetime, timedelta

from mcp.server.fastmcp import FastMCP

from .api_client import EODHDClient
from .data_processor import DataProcessor
from .exceptions import EODHDError, APIError, DataProcessingError
from .config import config


# Set up logging
logging.basicConfig(
    level=logging.DEBUG if config.debug else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastMCP server instance
mcp = FastMCP("eodhd-mcp-server")


@mcp.tool()
async def get_stock_price(
    symbol: str,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    exchange: str = "US"
) -> str:
    """
    Get End-of-Day stock price data (OHLCV) for a given symbol.
    
    Args:
        symbol: Stock symbol (e.g., 'AAPL', 'MSFT')
        from_date: Start date in YYYY-MM-DD format (optional)
        to_date: End date in YYYY-MM-DD format (optional)
        exchange: Exchange code (default: 'US')
    
    Returns:
        Formatted string containing stock price data
    """
    try:
        # Validate symbol
        if not symbol or not symbol.strip():
            return "Error: Symbol is required"
        
        symbol = symbol.strip().upper()
        
        # Set default date range if not provided (last 30 days)
        if not from_date and not to_date:
            to_date = datetime.now().strftime('%Y-%m-%d')
            from_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        logger.info(f"Fetching stock price for {symbol} from {from_date} to {to_date}")
        
        async with EODHDClient() as client:
            raw_data = await client.get_eod_data(symbol, from_date, to_date, exchange)
            
            if not raw_data:
                return f"No stock price data found for {symbol}"
            
            # Process the data
            df = DataProcessor.process_eod_data(raw_data)
            
            # Format for display
            result = DataProcessor.format_for_display(df, 'eod')
            return result
            
    except APIError as e:
        logger.error(f"API error in get_stock_price: {e}")
        return f"API Error: {e}"
    except DataProcessingError as e:
        logger.error(f"Data processing error in get_stock_price: {e}")
        return f"Data Processing Error: {e}"
    except Exception as e:
        logger.error(f"Unexpected error in get_stock_price: {e}")
        return f"Unexpected Error: {e}"


@mcp.tool()
async def get_earnings_calendar(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    symbols: Optional[str] = None
) -> str:
    """
    Get earnings calendar information for specified date range and/or symbols.
    
    Args:
        from_date: Start date in YYYY-MM-DD format (optional)
        to_date: End date in YYYY-MM-DD format (optional)
        symbols: Comma-separated list of symbols (optional)
    
    Returns:
        Formatted string containing earnings calendar data
    """
    try:
        # Set default date range if not provided (next 7 days)
        if not from_date and not to_date:
            from_date = datetime.now().strftime('%Y-%m-%d')
            to_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        
        logger.info(f"Fetching earnings calendar from {from_date} to {to_date} for symbols: {symbols}")
        
        async with EODHDClient() as client:
            raw_data = await client.get_earnings_calendar(from_date, to_date, symbols)
            
            if not raw_data:
                return f"No earnings calendar data found for the specified criteria"
            
            # Process the data
            df = DataProcessor.process_earnings_data(raw_data)
            
            # Format for display
            result = DataProcessor.format_for_display(df, 'earnings')
            return result
            
    except APIError as e:
        logger.error(f"API error in get_earnings_calendar: {e}")
        return f"API Error: {e}"
    except DataProcessingError as e:
        logger.error(f"Data processing error in get_earnings_calendar: {e}")
        return f"Data Processing Error: {e}"
    except Exception as e:
        logger.error(f"Unexpected error in get_earnings_calendar: {e}")
        return f"Unexpected Error: {e}"


@mcp.tool()
async def get_fundamentals(
    symbol: str,
    exchange: str = "US"
) -> str:
    """
    Get comprehensive fundamental data for a company.
    
    Args:
        symbol: Stock symbol (e.g., 'AAPL', 'MSFT')
        exchange: Exchange code (default: 'US')
    
    Returns:
        Formatted string containing fundamental data
    """
    try:
        # Validate symbol
        if not symbol or not symbol.strip():
            return "Error: Symbol is required"
        
        symbol = symbol.strip().upper()
        
        logger.info(f"Fetching fundamentals for {symbol}")
        
        async with EODHDClient() as client:
            raw_data = await client.get_fundamentals(symbol, exchange)
            
            if not raw_data:
                return f"No fundamental data found for {symbol}"
            
            # Process the data
            processed_data = DataProcessor.process_fundamentals_data(raw_data)
            
            # Format for display
            result = DataProcessor.format_for_display(processed_data, 'fundamentals')
            return result
            
    except APIError as e:
        logger.error(f"API error in get_fundamentals: {e}")
        return f"API Error: {e}"
    except DataProcessingError as e:
        logger.error(f"Data processing error in get_fundamentals: {e}")
        return f"Data Processing Error: {e}"
    except Exception as e:
        logger.error(f"Unexpected error in get_fundamentals: {e}")
        return f"Unexpected Error: {e}"


@mcp.tool()
async def get_index_components(
    index_code: str
) -> str:
    """
    Get the list of components (holdings) for a specific index.
    
    Args:
        index_code: Index code (e.g., 'MID.INDX', 'SML.INDX', 'GSPC.INDX')
    
    Returns:
        Formatted string containing index components data
    """
    try:
        # Validate index_code
        if not index_code or not index_code.strip():
            return "Error: Index code is required"
        
        index_code = index_code.strip().upper()
        
        # Ensure .INDX suffix
        if not index_code.endswith('.INDX'):
            index_code += '.INDX'
        
        logger.info(f"Fetching index components for {index_code}")
        
        async with EODHDClient() as client:
            raw_data = await client.get_index_components(index_code)
            
            if not raw_data:
                return f"No index components data found for {index_code}"
            
            # Process the data
            df = DataProcessor.process_index_components(raw_data)
            
            # Format for display
            result = DataProcessor.format_for_display(df, 'components')
            return result
            
    except APIError as e:
        logger.error(f"API error in get_index_components: {e}")
        return f"API Error: {e}"
    except DataProcessingError as e:
        logger.error(f"Data processing error in get_index_components: {e}")
        return f"Data Processing Error: {e}"
    except Exception as e:
        logger.error(f"Unexpected error in get_index_components: {e}")
        return f"Unexpected Error: {e}"


@mcp.tool()
async def get_growth_rates(
    symbol: str,
    exchange: str = "US"
) -> str:
    """
    Extract and display growth rate metrics from fundamental data.
    
    Args:
        symbol: Stock symbol (e.g., 'AAPL', 'MSFT')
        exchange: Exchange code (default: 'US')
    
    Returns:
        Formatted string containing growth rate metrics
    """
    try:
        # Validate symbol
        if not symbol or not symbol.strip():
            return "Error: Symbol is required"
        
        symbol = symbol.strip().upper()
        
        logger.info(f"Fetching growth rates for {symbol}")
        
        async with EODHDClient() as client:
            raw_data = await client.get_fundamentals(symbol, exchange)
            
            if not raw_data:
                return f"No fundamental data found for {symbol}"
            
            # Process the data
            processed_data = DataProcessor.process_fundamentals_data(raw_data)
            
            # Extract growth rates
            growth_rates = DataProcessor.extract_growth_rates(processed_data)
            
            if not growth_rates:
                return f"No growth rate data available for {symbol}"
            
            # Format growth rates for display
            formatted_lines = [f"Growth Rates for {symbol}:", "=" * 30]
            
            for metric, value in growth_rates.items():
                if value is not None:
                    formatted_lines.append(f"{metric.replace('_', ' ').title()}: {value}")
            
            return "\n".join(formatted_lines)
            
    except APIError as e:
        logger.error(f"API error in get_growth_rates: {e}")
        return f"API Error: {e}"
    except DataProcessingError as e:
        logger.error(f"Data processing error in get_growth_rates: {e}")
        return f"Data Processing Error: {e}"
    except Exception as e:
        logger.error(f"Unexpected error in get_growth_rates: {e}")
        return f"Unexpected Error: {e}"


def main():
    """Main entry point for the EODHD MCP Server."""
    try:
        logger.info("Starting EODHD MCP Server...")
        logger.info(f"Configuration loaded - API key configured: {bool(config.api_key)}")
        
        # Run the MCP server
        mcp.run()
        
    except Exception as e:
        logger.error(f"Failed to start EODHD MCP Server: {e}")
        raise


if __name__ == "__main__":
    main()