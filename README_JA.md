# EODHD MCP Server

*Language: [English](README.md) | 日本語*

EODHD金融APIへのアクセスを提供するModel Context Protocol (MCP)サーバーです。このサーバーにより、Claude Codeやその他のMCPクライアントが統一されたインターフェースを通じて株価、決算データ、ファンダメンタル情報、インデックス構成銘柄を取得できます。

## 機能

- **株価データ**: 過去の終値ベース（EOD）OHLCVデータを取得
- **決算カレンダー**: 決算発表スケジュールと予想値にアクセス
- **ファンダメンタルデータ**: 企業の包括的な財務指標を取得
- **インデックス構成銘柄**: 市場インデックスの構成銘柄情報を取得
- **成長指標**: 成長率データの抽出と分析
- **出来高分析**: 指定した期間の平均出来高と出来高比率を取得

## 利用可能なツール

### 1. `get_stock_price`
任意の銘柄の終値ベース株価データを取得します。

**パラメータ:**
- `symbol` (必須): 株式シンボル（例: 'AAPL', 'MSFT'）
- `from_date` (オプション): 開始日（YYYY-MM-DD形式）
- `to_date` (オプション): 終了日（YYYY-MM-DD形式）
- `exchange` (オプション): 取引所コード（デフォルト: 'US'）

### 2. `get_earnings_calendar`
指定された日付範囲と銘柄の決算カレンダー情報を取得します。

**パラメータ:**
- `from_date` (オプション): 開始日（YYYY-MM-DD形式）
- `to_date` (オプション): 終了日（YYYY-MM-DD形式）
- `symbols` (オプション): カンマ区切りの銘柄リスト

### 3. `get_fundamentals`
企業の包括的なファンダメンタルデータにアクセスします。

**パラメータ:**
- `symbol` (必須): 株式シンボル
- `exchange` (オプション): 取引所コード（デフォルト: 'US'）

### 4. `get_index_components`
市場インデックスの構成銘柄情報を取得します。

**パラメータ:**
- `index_code` (必須): インデックスコード（例: 'MID.INDX', 'SML.INDX'）

### 5. `get_growth_rates`
ファンダメンタルデータから成長率指標を抽出します。

**パラメータ:**
- `symbol` (必須): 株式シンボル
- `exchange` (オプション): 取引所コード（デフォルト: 'US'）

### 6. `get_volume_averages`
指定した期間（デフォルトは20日・60日）の平均出来高を計算し、20日/60日の比率を返します。

**パラメータ:**
- `symbol` (必須): 株式シンボル
- `periods` (オプション): カンマ区切りの期間リスト（例: "10,20,60"）
- `exchange` (オプション): 取引所コード（デフォルト: 'US'）

**例:**
```bash
get_volume_averages(symbol="AAPL")
get_volume_averages(symbol="TSLA", periods="10,30,90")
```

### 7. `get_earnings_trend`
過去 *n* 年間（デフォルト2年）の決算結果を取得し、EPS と売上が増加傾向かどうかを判定します。

**パラメータ:**
- `symbol` (必須): 株式シンボル
- `years` (オプション): 遡る年数（デフォルト: 2）
- `exchange` (オプション): 取引所コード（デフォルト: 'US'）

**例:**
```bash
get_earnings_trend(symbol="AAPL", years=2)
```

## インストール

### 前提条件
- Python 3.8以上
- EODHD APIキー（[eodhd.com](https://eodhd.com)でサインアップ）

### セットアップ

1. **プロジェクトのクローンとセットアップ:**
```bash
# リポジトリをクローン
git clone <repository-url>
cd eodhd-mcp-server

# 仮想環境を作成
python -m venv venv

# 仮想環境をアクティベート
source venv/bin/activate  # macOS/Linuxの場合
# または
venv\\Scripts\\activate     # Windowsの場合

# 依存関係をインストール
pip install -r requirements.txt

# パッケージを開発モードでインストール
pip install -e .
```

2. **環境変数の設定:**
```bash
# サンプル環境ファイルをコピー
cp .env.example .env

# .envファイルを編集してEODHD APIキーを追加
EODHD_API_KEY=your_actual_api_key_here
```

3. **インストールのテスト:**
```bash
# サーバーが正常に起動するかテスト（Ctrl+Cで停止）
eodhd-mcp-server

# 以下のような出力が表示されるはずです:
# 2024-06-28 16:04:42,657 - eodhd_mcp_server.server - INFO - Starting EODHD MCP Server...
# 2024-06-28 16:04:42,657 - eodhd_mcp_server.server - INFO - Configuration loaded - API key configured: True
```

## 使用方法

### MCPサーバーの実行

サーバーはstdioベースのMCPサーバーとして実行されます：

```bash
eodhd-mcp-server
```

### Cursorとの統合

Cursorの MCP設定（`~/.cursor/mcp.json`）にサーバーを追加します：

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

**重要な設定のポイント:**
- `/path/to/your/project/` を実際のプロジェクトパスに置き換える
- 仮想環境内の`eodhd-mcp-server`実行ファイルの絶対パスを使用
- `cwd`（カレントワーキングディレクトリ）をプロジェクトルートに設定
- `env`セクションに必要な環境変数をすべて含める
- `your_api_key_here`を実際のEODHD APIキーに置き換える

**代替方法: .envファイルの使用**
セキュリティの観点から`.env`ファイルを使用する場合（推奨）、設定を簡素化できます：

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

`.env`ファイルに必要な環境変数がすべて含まれていることを確認してください。

### Cursorでの使用例

MCPサーバーが設定され実行されている場合（緑のアイコン）、Cursorでツールを使用できます：

**株価データ:**
- "AAPLの過去30日間の株価を取得して"
- "今年のTeslaの株価パフォーマンスを表示して"

**決算情報:**
- "今週の決算発表を表示して"
- "AAPLの過去10回の決算結果を取得して"

**ファンダメンタル分析:**
- "Microsoftのファンダメンタルデータを取得して"
- "NVDAの成長率を表示して"

**インデックス構成銘柄:**
- "S&P 500の構成銘柄は何ですか？"
- "Russell 2000の保有銘柄を表示して"

サーバーが自動的にAPI呼び出しを処理し、フォーマットされた読みやすい結果を返します。

## 設定

### 環境変数

- `EODHD_API_KEY`: EODHD APIキー（必須）
- `EODHD_BASE_URL`: EODHD APIのベースURL（デフォルト: https://eodhd.com/api）
- `REQUEST_TIMEOUT`: リクエストタイムアウト（秒）（デフォルト: 30）
- `MAX_RETRIES`: 最大リトライ回数（デフォルト: 3）
- `RATE_LIMIT_DELAY`: リクエスト間の遅延（秒）（デフォルト: 0.1）
- `DEBUG`: デバッグログの有効化（デフォルト: false）

### APIキー

[EODHD](https://eodhd.com/)から無料のAPIキーを取得します：
1. アカウントにサインアップ
2. APIセクションに移動
3. APIキーをコピー
4. `.env`ファイルに追加

## エラーハンドリング

サーバーには以下の包括的なエラーハンドリングが含まれています：

- **APIエラー**: 無効なAPIキー、レート制限、データなし
- **ネットワークエラー**: 接続タイムアウト、ネットワーク障害
- **データ処理エラー**: 無効なデータ形式、解析失敗
- **設定エラー**: APIキーなし、無効なパラメータ

## 開発

### プロジェクト構造

```
eodhd-mcp-server/
├── src/eodhd_mcp_server/
│   ├── __init__.py          # パッケージ初期化
│   ├── server.py            # ツール付きメインMCPサーバー
│   ├── api_client.py        # EODHD APIクライアント
│   ├── data_processor.py    # データ処理ユーティリティ
│   ├── config.py            # 設定管理
│   └── exceptions.py        # カスタム例外
├── tests/                   # テストファイル（実装予定）
├── requirements.txt         # Python依存関係
├── pyproject.toml          # パッケージ設定
├── .env.example            # サンプル環境ファイル
└── README.md               # このファイル
```

### テストの実行

```bash
# テスト依存関係をインストール
pip install pytest pytest-asyncio

# テストを実行
pytest tests/
```

### 貢献

1. リポジトリをフォーク
2. 機能ブランチを作成
3. 変更を加える
4. 新機能のテストを追加
5. プルリクエストを提出

## API互換性

このサーバーは既存のstocktradingコードベースとの互換性を以下により維持します：

- 既存コードで使用されるDataFrame構造の保持
- 一貫した列名とデータ型の維持
- 同じAPIレスポンス形式のサポート
- 確立されたエラーハンドリングパターンの踏襲

## ライセンス

MIT License - 詳細はLICENSEファイルを参照してください。

## トラブルシューティング

### Cursorで赤いアイコン（サーバーが動作しない）

CursorでEODHD MCPサーバーの横に赤いアイコンが表示される場合：

1. **設定パスを確認**: `command`パスが正しい場所を指していることを確認：
   ```bash
   # 正しいパスを見つける
   source venv/bin/activate
   which eodhd-mcp-server
   ```

2. **環境変数を確認**: `.env`ファイルが存在し、以下が含まれていることを確認：
   ```
   EODHD_API_KEY=your_actual_api_key
   ```

3. **サーバーを手動でテスト**: サーバーを直接実行してみる：
   ```bash
   source venv/bin/activate
   eodhd-mcp-server
   ```

4. **Cursor設定を確認**: `~/.cursor/mcp.json`に以下が含まれていることを確認：
   - 実行ファイルへの絶対パス
   - 正しい作業ディレクトリ（`cwd`）
   - 環境変数または`.env`ファイルアクセス

5. **Cursorを再起動**: 設定変更後、Cursorを完全に再起動する

### よくある問題

- **APIキーの問題**: EODHD APIキーが有効で十分なクォータがあることを確認
- **パスの問題**: Cursor設定で絶対パスを使用
- **権限の問題**: 実行ファイルに適切な権限があることを確認
- **仮想環境**: 正しい仮想環境パスを使用していることを確認

## サポート

問題や質問について：
1. [EODHD APIドキュメント](https://eodhd.com/financial-api/)を確認
2. デバッグモード（`DEBUG=true`）でエラーメッセージを確認
3. 上記のトラブルシューティングガイドを使用
4. リポジトリでissueを開く

## 変更履歴

### バージョン 1.0.0
- 初回リリース
- 株価、決算カレンダー、ファンダメンタル、インデックス構成銘柄のサポート
- 包括的なエラーハンドリングとデータ処理
- FastMCPとのMCPプロトコル統合 