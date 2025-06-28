# EODHD API MCP Server 設計書

## 1. 概要

### 1.1 目的
- EODHDの各種APIエンドポイントにアクセスするためのMCPサーバーを構築
- 株価データ、決算情報、ファンダメンタルデータの統一されたインターフェースを提供

### 1.2 技術スタック
- **言語**: Python 3.8+
- **MCPフレームワーク**: `mcp` (Model Context Protocol)
- **HTTP クライアント**: `requests`
- **データ処理**: `pandas`
- **環境変数管理**: `python-dotenv`

## 2. アーキテクチャ設計

### 2.1 システム構成
```
┌─────────────────────────────────────┐
│           MCP Client                │
│        (Claude Code等)             │
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

### 2.2 ディレクトリ構造
```
eodhd_mcp_server/
├── README.md
├── requirements.txt
├── setup.py
├── src/
│   └── eodhd_mcp_server/
│       ├── __init__.py
│       ├── server.py           # メインサーバー
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

## 3. MCPツール定義

### 3.1 stock_price ツール
```json
{
  "name": "stock_price",
  "description": "株価データ（OHLCV）を取得",
  "inputSchema": {
    "type": "object",
    "properties": {
      "symbol": {
        "type": "string",
        "description": "株式シンボル（例: AAPL, MSFT）"
      },
      "from_date": {
        "type": "string",
        "description": "開始日（YYYY-MM-DD形式）"
      },
      "to_date": {
        "type": "string", 
        "description": "終了日（YYYY-MM-DD形式）"
      },
      "exchange": {
        "type": "string",
        "description": "取引所コード（デフォルト: US）",
        "default": "US"
      }
    },
    "required": ["symbol"]
  }
}
```

### 3.2 earnings_calendar ツール
```json
{
  "name": "earnings_calendar",
  "description": "決算カレンダー情報を取得",
  "inputSchema": {
    "type": "object",
    "properties": {
      "from_date": {
        "type": "string",
        "description": "開始日（YYYY-MM-DD形式）"
      },
      "to_date": {
        "type": "string",
        "description": "終了日（YYYY-MM-DD形式）"
      },
      "symbols": {
        "type": "string",
        "description": "特定の銘柄（カンマ区切り、オプション）"
      }
    }
  }
}
```

### 3.3 fundamentals ツール
```json
{
  "name": "fundamentals",
  "description": "企業のファンダメンタルデータを取得",
  "inputSchema": {
    "type": "object", 
    "properties": {
      "symbol": {
        "type": "string",
        "description": "株式シンボル"
      },
      "exchange": {
        "type": "string",
        "description": "取引所コード（デフォルト: US）",
        "default": "US"
      }
    },
    "required": ["symbol"]
  }
}
```

### 3.4 index_components ツール
```json
{
  "name": "index_components",
  "description": "インデックス構成銘柄を取得",
  "inputSchema": {
    "type": "object",
    "properties": {
      "index_code": {
        "type": "string",
        "description": "インデックスコード（例: MID.INDX, SML.INDX）"
      }
    },
    "required": ["index_code"]
  }
}
```

## 4. 実装仕様

### 4.1 メインサーバー (server.py)
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
        # ツールの登録
        self.server.list_tools = self._list_tools
        self.server.call_tool = self._call_tool
    
    async def _list_tools(self):
        # 利用可能なツールのリストを返す
        pass
    
    async def _call_tool(self, name: str, arguments: dict):
        # ツールの実行
        pass
```

### 4.2 EODHD APIサービス (services/eodhd_api.py)
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
        """リトライ戦略付きのセッションを作成"""
        session = requests.Session()
        # リトライ設定の実装
        return session
    
    async def get_eod_data(self, symbol: str, from_date: str = None, 
                          to_date: str = None, exchange: str = "US") -> Dict[str, Any]:
        """株価データを取得"""
        pass
    
    async def get_earnings_calendar(self, from_date: str = None, 
                                  to_date: str = None, symbols: str = None) -> Dict[str, Any]:
        """決算カレンダーを取得"""
        pass
    
    async def get_fundamentals(self, symbol: str, exchange: str = "US") -> Dict[str, Any]:
        """ファンダメンタルデータを取得"""
        pass
    
    async def get_index_components(self, index_code: str) -> Dict[str, Any]:
        """インデックス構成銘柄を取得"""
        pass
```

### 4.3 データプロセッサー (services/data_processor.py)
```python
import pandas as pd
from typing import Dict, Any, List

class DataProcessor:
    @staticmethod
    def process_eod_data(raw_data: List[Dict]) -> pd.DataFrame:
        """EODデータをDataFrameに変換"""
        pass
    
    @staticmethod
    def process_earnings_data(raw_data: Dict) -> pd.DataFrame:
        """決算データをDataFrameに変換"""
        pass
    
    @staticmethod
    def process_fundamentals_data(raw_data: Dict) -> Dict[str, Any]:
        """ファンダメンタルデータを構造化"""
        pass
    
    @staticmethod
    def extract_growth_rates(fundamentals: Dict) -> Dict[str, str]:
        """成長率データを抽出"""
        pass
```

### 4.4 設定管理 (utils/config.py)
```python
import os
from dotenv import load_dotenv
from typing import Dict, Any

def load_config() -> Dict[str, Any]:
    """環境変数から設定を読み込み"""
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

## 5. エラーハンドリング

### 5.1 エラー分類
- **APIエラー**: レート制限、認証エラー、データなし
- **ネットワークエラー**: タイムアウト、接続エラー
- **データエラー**: 不正な形式、欠損データ
- **設定エラー**: APIキー未設定、不正なパラメータ

### 5.2 エラーハンドラー (services/error_handler.py)
```python
import logging
from typing import Optional
import requests

class EODHDErrorHandler:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def handle_api_error(self, response: requests.Response) -> Optional[Exception]:
        """APIエラーを処理"""
        if response.status_code == 401:
            return ValueError("Invalid API key")
        elif response.status_code == 429:
            return ValueError("API rate limit exceeded")
        elif response.status_code == 404:
            return ValueError("Data not found")
        return None
    
    def handle_network_error(self, error: Exception) -> Exception:
        """ネットワークエラーを処理"""
        return ConnectionError(f"Network error: {str(error)}")
```

## 6. セキュリティ考慮事項

### 6.1 APIキー管理
- 環境変数での管理（`.env`ファイル）
- ログ出力時のAPIキー秘匿化
- キー検証機能の実装

### 6.2 レート制限対応
- APIコール頻度の制御
- 自動リトライ機能
- エラー時の適切な待機時間

## 7. テスト戦略

### 7.1 単体テスト
- 各ツールの機能テスト
- APIサービスのモックテスト
- データプロセッサーのテスト

### 7.2 統合テスト
- 実際のEODHD APIとの連携テスト
- MCPプロトコルのテスト

## 8. デプロイメント

### 8.1 パッケージング
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

### 8.2 インストール手順
```bash
# 開発環境での実行
cd eodhd_mcp_server
pip install -e .

# 本番環境での実行
pip install eodhd-mcp-server
```

## 9. 使用例

### 9.1 MCPクライアントでの利用
```python
# Claude Codeからの利用例
tools = mcp_client.list_tools()
result = mcp_client.call_tool("stock_price", {
    "symbol": "AAPL",
    "from_date": "2024-01-01",
    "to_date": "2024-12-31"
})
```

