import asyncio
from datetime import datetime, timedelta

import pandas as pd
import pytest

from eodhd_mcp_server.data_processor import DataProcessor
from eodhd_mcp_server.server import get_volume_averages


@pytest.mark.parametrize("periods,expected", [
    ([20, 60], {20: sum(range(41, 61)) / 20, 60: sum(range(1, 61)) / 60}),
    ([10], {10: sum(range(51, 61)) / 10}),
])
def test_calculate_average_volume(periods, expected):
    # Prepare 60 days of synthetic volume data 1..60
    dates = pd.date_range(datetime.today() - timedelta(days=59), periods=60)
    df = pd.DataFrame({"date": dates, "volume": range(1, 61)})

    result = DataProcessor.calculate_average_volume(df, periods)
    for p in periods:
        assert pytest.approx(result[p], rel=1e-6) == expected[p]


@pytest.mark.asyncio
async def test_get_volume_averages_tool(monkeypatch):
    """Test the MCP tool with mocked API client to avoid external requests."""

    # Create mock raw data for 80 days
    today = datetime.now().date()
    raw_data = []
    for i in range(80):
        day = today - timedelta(days=79 - i)
        raw_data.append({
            "date": day.strftime("%Y-%m-%d"),
            "open": 1, "high": 1, "low": 1, "close": 1,
            "volume": i + 1,
        })

    async def mock_get_eod_data(self, symbol, from_date, to_date, exchange):
        return raw_data

    # Patch EODHDClient.get_eod_data
    from eodhd_mcp_server.api_client import EODHDClient
    monkeypatch.setattr(EODHDClient, "get_eod_data", mock_get_eod_data, raising=True)

    result = await get_volume_averages(symbol="TEST", periods="20,60")
    assert "20-day Avg Volume" in result
    assert "60-day Avg Volume" in result
    assert "Volume Ratio" in result 