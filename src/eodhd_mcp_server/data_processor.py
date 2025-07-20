"""Data processing utilities for EODHD API responses."""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

import pandas as pd

from .exceptions import DataProcessingError


logger = logging.getLogger(__name__)


class DataProcessor:
    """Utility class for processing EODHD API responses."""
    
    @staticmethod
    def process_eod_data(raw_data: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Process End-of-Day stock price data into a DataFrame.
        
        Args:
            raw_data: Raw EOD data from EODHD API
            
        Returns:
            DataFrame with OHLCV data
        """
        try:
            if not raw_data:
                return pd.DataFrame()
            
            df = pd.DataFrame(raw_data)
            
            # Ensure required columns exist
            required_columns = ['date', 'open', 'high', 'low', 'close', 'volume']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                logger.warning(f"Missing columns in EOD data: {missing_columns}")
                # Add missing columns with default values
                for col in missing_columns:
                    df[col] = None
            
            # Convert date column to datetime
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                df = df.sort_values('date')
            
            # Ensure numeric columns are properly typed
            numeric_columns = ['open', 'high', 'low', 'close', 'volume']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Reset index
            df = df.reset_index(drop=True)
            
            return df
            
        except Exception as e:
            raise DataProcessingError(f"Failed to process EOD data: {e}")
    
    @staticmethod
    def process_earnings_data(raw_data: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Process earnings calendar data into a DataFrame.
        
        Args:
            raw_data: Raw earnings data from EODHD API
            
        Returns:
            DataFrame with earnings calendar data
        """
        try:
            if not raw_data:
                return pd.DataFrame()
            
            df = pd.DataFrame(raw_data)
            
            # Convert date column to datetime if present
            date_columns = ['date', 'report_date', 'earnings_date']
            for col in date_columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            
            # Convert numeric columns
            numeric_columns = ['estimate', 'actual', 'difference', 'surprise_pct']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Sort by date if available
            if 'date' in df.columns:
                df = df.sort_values('date')
            elif 'report_date' in df.columns:
                df = df.sort_values('report_date')
            elif 'earnings_date' in df.columns:
                df = df.sort_values('earnings_date')
            
            # Reset index
            df = df.reset_index(drop=True)
            
            return df
            
        except Exception as e:
            raise DataProcessingError(f"Failed to process earnings data: {e}")
    
    @staticmethod
    def process_fundamentals_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process and structure fundamental data.
        
        Args:
            raw_data: Raw fundamental data from EODHD API
            
        Returns:
            Structured fundamental data dictionary
        """
        try:
            if not raw_data:
                return {}
            
            processed_data = {}
            
            # Extract general information
            general_info = raw_data.get('General', {})
            if general_info:
                processed_data['general'] = {
                    'code': general_info.get('Code'),
                    'name': general_info.get('Name'),
                    'type': general_info.get('Type'),
                    'country': general_info.get('CountryName'),
                    'currency': general_info.get('CurrencyCode'),
                    'exchange': general_info.get('Exchange'),
                    'sector': general_info.get('Sector'),
                    'industry': general_info.get('Industry'),
                    'description': general_info.get('Description'),
                    'website': general_info.get('WebURL'),
                    'market_cap': general_info.get('MarketCapitalization'),
                    'shares_outstanding': general_info.get('SharesOutstanding'),
                    'employees': general_info.get('FullTimeEmployees')
                }
            
            # Extract highlights
            highlights = raw_data.get('Highlights', {})
            if highlights:
                processed_data['highlights'] = {
                    'market_cap': highlights.get('MarketCapitalization'),
                    'ebitda': highlights.get('EBITDA'),
                    'pe_ratio': highlights.get('PERatio'),
                    'peg_ratio': highlights.get('PEGRatio'),
                    'wall_street_target_price': highlights.get('WallStreetTargetPrice'),
                    'book_value': highlights.get('BookValue'),
                    'dividend_share': highlights.get('DividendShare'),
                    'dividend_yield': highlights.get('DividendYield'),
                    'earnings_share': highlights.get('EarningsShare'),
                    'eps_estimate_current_year': highlights.get('EPSEstimateCurrentYear'),
                    'eps_estimate_next_year': highlights.get('EPSEstimateNextYear'),
                    'eps_estimate_next_quarter': highlights.get('EPSEstimateNextQuarter'),
                    'eps_estimate_current_quarter': highlights.get('EPSEstimateCurrentQuarter'),
                    'most_recent_quarter': highlights.get('MostRecentQuarter'),
                    'profit_margin': highlights.get('ProfitMargin'),
                    'operating_margin_ttm': highlights.get('OperatingMarginTTM'),
                    'return_on_assets_ttm': highlights.get('ReturnOnAssetsTTM'),
                    'return_on_equity_ttm': highlights.get('ReturnOnEquityTTM'),
                    'revenue_ttm': highlights.get('RevenueTTM'),
                    'revenue_per_share_ttm': highlights.get('RevenuePerShareTTM'),
                    'quarterly_revenue_growth_yoy': highlights.get('QuarterlyRevenueGrowthYOY'),
                    'gross_profit_ttm': highlights.get('GrossProfitTTM'),
                    'diluted_eps_ttm': highlights.get('DilutedEpsTTM'),
                    'quarterly_earnings_growth_yoy': highlights.get('QuarterlyEarningsGrowthYOY')
                }
            
            # Extract valuation metrics
            valuation = raw_data.get('Valuation', {})
            if valuation:
                processed_data['valuation'] = valuation
            
            # Extract financial statements
            if 'Financials' in raw_data:
                processed_data['financials'] = raw_data['Financials']
            
            # Extract technical data
            if 'Technicals' in raw_data:
                processed_data['technicals'] = raw_data['Technicals']
            
            return processed_data
            
        except Exception as e:
            raise DataProcessingError(f"Failed to process fundamental data: {e}")
    
    @staticmethod
    def extract_growth_rates(fundamentals: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract growth rate information from fundamental data.
        
        Args:
            fundamentals: Processed fundamental data
            
        Returns:
            Dictionary containing growth rate metrics
        """
        try:
            growth_rates = {}
            
            # Extract from highlights
            highlights = fundamentals.get('highlights', {})
            if highlights:
                growth_rates.update({
                    'quarterly_revenue_growth_yoy': highlights.get('quarterly_revenue_growth_yoy'),
                    'quarterly_earnings_growth_yoy': highlights.get('quarterly_earnings_growth_yoy')
                })
            
            # Extract from financials if available
            financials = fundamentals.get('financials', {})
            if financials:
                # You could add more sophisticated growth rate calculations here
                # based on historical financial data
                pass
            
            return growth_rates
            
        except Exception as e:
            raise DataProcessingError(f"Failed to extract growth rates: {e}")
    
    @staticmethod
    def process_index_components(raw_data: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Process index components data into a DataFrame.
        
        Args:
            raw_data: Raw index components data from EODHD API
            
        Returns:
            DataFrame with index components data
        """
        try:
            if not raw_data:
                return pd.DataFrame()
            
            df = pd.DataFrame(raw_data)
            
            # Ensure symbol column exists
            if 'symbol' not in df.columns and 'Symbol' in df.columns:
                df['symbol'] = df['Symbol']
            elif 'symbol' not in df.columns and 'Code' in df.columns:
                df['symbol'] = df['Code']
            
            # Convert numeric columns
            numeric_columns = ['weight', 'Weight', 'shares', 'Shares', 'market_value', 'MarketValue']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Sort by weight if available
            weight_columns = ['weight', 'Weight']
            for col in weight_columns:
                if col in df.columns:
                    df = df.sort_values(col, ascending=False)
                    break
            
            # Reset index
            df = df.reset_index(drop=True)
            
            return df
            
        except Exception as e:
            raise DataProcessingError(f"Failed to process index components data: {e}")
    
    @staticmethod
    def format_for_display(data: Any, data_type: str) -> str:
        """
        Format data for display in MCP response.
        
        Args:
            data: Data to format (DataFrame, dict, etc.)
            data_type: Type of data ('eod', 'earnings', 'fundamentals', 'components')
            
        Returns:
            Formatted string representation
        """
        try:
            if isinstance(data, pd.DataFrame):
                if data.empty:
                    return f"No {data_type} data available."
                
                # Format DataFrame based on type
                if data_type == 'eod':
                    return f"Stock Price Data ({len(data)} records):\n" + data.to_string(index=False)
                elif data_type == 'earnings':
                    return f"Earnings Calendar ({len(data)} records):\n" + data.to_string(index=False)
                elif data_type == 'components':
                    return f"Index Components ({len(data)} records):\n" + data.to_string(index=False)
                else:
                    return data.to_string(index=False)
            
            elif isinstance(data, dict):
                if data_type == 'fundamentals':
                    # Format fundamental data nicely
                    formatted_lines = []
                    
                    if 'general' in data:
                        general = data['general']
                        formatted_lines.append("=== GENERAL INFORMATION ===")
                        formatted_lines.append(f"Company: {general.get('name', 'N/A')}")
                        formatted_lines.append(f"Symbol: {general.get('code', 'N/A')}")
                        formatted_lines.append(f"Sector: {general.get('sector', 'N/A')}")
                        formatted_lines.append(f"Industry: {general.get('industry', 'N/A')}")
                        formatted_lines.append(f"Market Cap: {general.get('market_cap', 'N/A')}")
                        formatted_lines.append("")
                    
                    if 'highlights' in data:
                        highlights = data['highlights']
                        formatted_lines.append("=== KEY METRICS ===")
                        formatted_lines.append(f"P/E Ratio: {highlights.get('pe_ratio', 'N/A')}")
                        formatted_lines.append(f"EPS (TTM): {highlights.get('diluted_eps_ttm', 'N/A')}")
                        formatted_lines.append(f"Revenue (TTM): {highlights.get('revenue_ttm', 'N/A')}")
                        formatted_lines.append(f"Profit Margin: {highlights.get('profit_margin', 'N/A')}")
                        formatted_lines.append(f"Dividend Yield: {highlights.get('dividend_yield', 'N/A')}")
                    
                    return "\n".join(formatted_lines)
                else:
                    return str(data)
            
            else:
                return str(data)
                
        except Exception as e:
            logger.error(f"Failed to format data for display: {e}")
            return f"Error formatting {data_type} data: {e}"

    @staticmethod
    def calculate_average_volume(df: pd.DataFrame, periods: Optional[List[int]] = None) -> Dict[int, Optional[float]]:
        """
        Calculate average trading volume for specified periods.

        Args:
            df: DataFrame containing at least a 'volume' column, sorted by date ascending.
            periods: List of periods (in trading days) to calculate averages for. Defaults to [20, 60].

        Returns:
            Dictionary mapping period -> average volume (or None if insufficient data).
        """
        if periods is None:
            periods = [20, 60]

        if df.empty or 'volume' not in df.columns:
            return {p: None for p in periods}

        # Ensure df sorted by date ascending
        if 'date' in df.columns:
            df = df.sort_values('date')

        averages: Dict[int, Optional[float]] = {}
        for p in periods:
            if len(df) >= p:
                averages[p] = df['volume'].tail(p).mean()
            else:
                averages[p] = None
        return averages

    @staticmethod
    def _determine_trend(series: pd.Series) -> str:
        """Return 'increasing', 'decreasing', 'mixed', or 'N/A' for given numeric series."""
        if series.isna().all():
            return 'N/A'
        diffs = series.diff().dropna()
        if diffs.empty:
            return 'N/A'
        if (diffs > 0).all():
            return 'increasing'
        if (diffs < 0).all():
            return 'decreasing'
        return 'mixed'

    @staticmethod
    def analyze_earnings_trend(df: pd.DataFrame) -> Dict[str, str]:
        """
        Analyse EPS and revenue trend in earnings DataFrame.

        The function expects columns like 'actual' (EPS actual) and either
        'revenue' or 'revenue_actual'. It determines whether each metric is
        increasing, decreasing or mixed over time.
        """
        if df.empty:
            return {}

        # Ensure sorted by date ascending
        if 'report_date' in df.columns:
            df = df.sort_values('report_date')
        elif 'date' in df.columns:
            df = df.sort_values('date')

        result: Dict[str, str] = {}
        if 'actual' in df.columns:
            result['eps_trend'] = DataProcessor._determine_trend(pd.to_numeric(df['actual'], errors='coerce'))
        elif 'eps' in df.columns:
            result['eps_trend'] = DataProcessor._determine_trend(pd.to_numeric(df['eps'], errors='coerce'))

        # revenue column variations
        rev_col = None
        for cand in ['revenue', 'revenue_actual', 'revenueActual']:
            if cand in df.columns:
                rev_col = cand
                break
        if rev_col:
            result['revenue_trend'] = DataProcessor._determine_trend(pd.to_numeric(df[rev_col], errors='coerce'))

        return result