# セットアップガイド

## 1. 事前準備

### 1.1 必要なAPIキーの取得

#### Alpha Vantage API（株価データ用）
1. [Alpha Vantage](https://www.alphavantage.co/support/#api-key) でAPIキーを取得
2. 無料プランでは1日500リクエスト、1分間5リクエストの制限

#### NewsAPI（ニュースデータ用）
1. [NewsAPI](https://newsapi.org/register) でAPIキーを取得
2. 無料プランでは1日1000リクエストの制限

#### Google API（Google Docs用）
1. [Google Cloud Console](https://console.cloud.google.com/) でプロジェクト作成
2. Google Drive API と Google Docs API を有効化
3. サービスアカウントを作成し、JSONキーをダウンロード

### 1.2 Power Automate環境の準備
1. Microsoft 365 Business または個人アカウントでPower Automateにアクセス
2. 必要なコネクタの接続確認
   - OneDrive/SharePoint
   - Office 365 Outlook
   - Microsoft Teams
   - HTTP（外部API用）

## 2. 設定情報の入力

以下の情報を`config/settings.json`に入力してください：

### 2.1 売上データ関連
```json
"sales_data": {
  "folder_path": "ここに実際のフォルダパスを入力",
  "file_pattern": "*.csv"
}
```

**必要な情報をお聞かせください：**
- OneDrive/SharePointの売上データフォルダのパスまたはID
- CSVファイルの命名規則
- CSVファイルの列構造（どのような項目があるか）

### 2.2 株価データ関連
```json
"stock_data": {
  "api_key": "ここにAlpha Vantage APIキーを入力",
  "tickers": ["監視対象の株式ティッカーを入力"]
}
```

**必要な情報をお聞かせください：**
- 監視したい株式のティッカーシンボル（例：AAPL, GOOGL, MSFT等）

### 2.3 Google Docs関連
```json
"google_docs": {
  "template_id": "ここにテンプレートのGoogle DocsドキュメントIDを入力",
  "output_folder": "/Weekly Reports/"
}
```

**必要な情報をお聞かせください：**
- レポートテンプレートのGoogle DocsドキュメントID
- レポート保存先のGoogle Driveフォルダ

### 2.4 Teams関連
```json
"teams": {
  "chat_id": "ここにJunyaさんのTeams Chat IDを入力"
}
```

**必要な情報をお聞かせください：**
- JunyaさんのTeams Chat ID（プライベートチャット用）

## 3. テスト実行

### 3.1 データ処理スクリプトのテスト
```bash
cd weeklybrief
python scripts/data-processing.py
```

### 3.2 Power Automateフローのテスト
1. フローを手動実行
2. 各ステップの動作確認
3. エラーログの確認

## 4. 本番運用開始

1. スケジュール実行の有効化
2. エラー通知設定の確認
3. 初回実行の監視

## トラブルシューティング

### よくある問題
1. **APIキーが無効**: 各APIキーが正しく設定されているか確認
2. **権限エラー**: Google Drive、OneDriveへのアクセス権限を確認
3. **レートリミット**: API呼び出し回数制限に達していないか確認

### サポート連絡先
- 技術的な問題: [開発担当者メール]
- 運用に関する問題: [プロジェクトオーナー] 