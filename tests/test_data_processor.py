"""Tests for data processor module."""

import pytest
import pandas as pd
from datetime import datetime

from eodhd_mcp_server.data_processor import DataProcessor
from eodhd_mcp_server.exceptions import DataProcessingError


class TestDataProcessor:
    """Test class for DataProcessor."""
    
    def test_process_eod_data_empty(self):
        """Test processing empty EOD data."""
        result = DataProcessor.process_eod_data([])
        assert isinstance(result, pd.DataFrame)
        assert result.empty
    
    def test_process_eod_data_valid(self):
        """Test processing valid EOD data."""
        sample_data = [
            {
                'date': '2024-01-01',
                'open': 150.0,
                'high': 155.0,
                'low': 149.0,
                'close': 154.0,
                'volume': 1000000
            },
            {
                'date': '2024-01-02',
                'open': 154.0,
                'high': 158.0,
                'low': 153.0,
                'close': 157.0,
                'volume': 1200000
            }
        ]
        
        result = DataProcessor.process_eod_data(sample_data)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert all(col in result.columns for col in ['date', 'open', 'high', 'low', 'close', 'volume'])
        assert pd.api.types.is_datetime64_any_dtype(result['date'])
        assert pd.api.types.is_numeric_dtype(result['open'])
    
    def test_process_earnings_data_empty(self):
        """Test processing empty earnings data."""
        result = DataProcessor.process_earnings_data([])
        assert isinstance(result, pd.DataFrame)
        assert result.empty
    
    def test_process_earnings_data_valid(self):
        """Test processing valid earnings data."""
        sample_data = [
            {
                'symbol': 'AAPL',
                'date': '2024-01-15',
                'estimate': 2.50,
                'actual': 2.65,
                'surprise_pct': 6.0
            },
            {
                'symbol': 'MSFT',
                'date': '2024-01-16',
                'estimate': 3.20,
                'actual': 3.15,
                'surprise_pct': -1.6
            }
        ]
        
        result = DataProcessor.process_earnings_data(sample_data)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert 'symbol' in result.columns
        assert pd.api.types.is_datetime64_any_dtype(result['date'])
    
    def test_process_fundamentals_data_empty(self):
        """Test processing empty fundamentals data."""
        result = DataProcessor.process_fundamentals_data({})
        assert isinstance(result, dict)
        assert result == {}
    
    def test_process_fundamentals_data_valid(self):
        """Test processing valid fundamentals data."""
        sample_data = {
            'General': {
                'Code': 'AAPL',
                'Name': 'Apple Inc.',
                'Type': 'Common Stock',
                'CountryName': 'USA',
                'CurrencyCode': 'USD',
                'Exchange': 'NASDAQ',
                'Sector': 'Technology',
                'Industry': 'Consumer Electronics'
            },
            'Highlights': {
                'MarketCapitalization': 3000000000000,
                'PERatio': 25.5,
                'DividendYield': 0.005,
                'EarningsShare': 6.15
            }
        }
        
        result = DataProcessor.process_fundamentals_data(sample_data)
        
        assert isinstance(result, dict)
        assert 'general' in result
        assert 'highlights' in result
        assert result['general']['code'] == 'AAPL'
        assert result['general']['name'] == 'Apple Inc.'
        assert result['highlights']['pe_ratio'] == 25.5
    
    def test_process_index_components_empty(self):
        """Test processing empty index components data."""
        result = DataProcessor.process_index_components([])
        assert isinstance(result, pd.DataFrame)
        assert result.empty
    
    def test_extract_growth_rates(self):
        """Test growth rates extraction."""
        fundamentals_data = {
            'highlights': {
                'quarterly_revenue_growth_yoy': 0.15,
                'quarterly_earnings_growth_yoy': 0.08
            }
        }
        
        result = DataProcessor.extract_growth_rates(fundamentals_data)
        
        assert isinstance(result, dict)
        assert 'quarterly_revenue_growth_yoy' in result
        assert 'quarterly_earnings_growth_yoy' in result
        assert result['quarterly_revenue_growth_yoy'] == 0.15
    
    def test_format_for_display_dataframe(self):
        """Test formatting DataFrame for display."""
        df = pd.DataFrame({
            'symbol': ['AAPL', 'MSFT'],
            'price': [150.0, 300.0]
        })
        
        result = DataProcessor.format_for_display(df, 'eod')
        
        assert isinstance(result, str)
        assert 'Stock Price Data' in result
        assert 'AAPL' in result
        assert 'MSFT' in result
    
    def test_format_for_display_empty_dataframe(self):
        """Test formatting empty DataFrame for display."""
        df = pd.DataFrame()
        
        result = DataProcessor.format_for_display(df, 'eod')
        
        assert isinstance(result, str)
        assert 'No eod data available' in result