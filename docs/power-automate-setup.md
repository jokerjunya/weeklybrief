# Power Automate フロー構築ガイド

## 概要
週次レポート自動化のためのPower Automateフローを構築します。

## 事前準備

### 1. 必要なAPIキーの取得
- **Alpha Vantage API**: 無料登録で1日500リクエスト
  - [https://www.alphavantage.co/support/#api-key](https://www.alphavantage.co/support/#api-key)
- **NewsAPI**: 無料登録で1日1000リクエスト
  - [https://newsapi.org/register](https://newsapi.org/register)

### 2. Teams Chat ID の取得
詳細は `docs/teams-chat-id-guide.md` を参照

## メインフロー構築手順

### Phase 1: 基本フロー作成

#### 1. 新しいフロー作成
1. Power Automate ([make.powerautomate.com](https://make.powerautomate.com)) にアクセス
2. **マイフロー** → **新しいフロー** → **定期的なクラウドフロー**
3. フロー名: `週次レポート自動生成`
4. **繰り返し**設定:
   - 間隔: 1
   - 単位: 週
   - 設定されている日: 月曜日
   - 設定されている時刻: 8:00 AM
   - タイムゾーン: (UTC+09:00) 大阪、札幌、東京

#### 2. 変数初期化
**変数を初期化する** アクションを追加:
```
名前: CurrentDate
種類: 文字列
値: formatDateTime(utcNow(), 'yyyy-MM-dd')
```

### Phase 2: データ収集

#### 3. 売上データ取得
**OneDrive for Business** → **ファイルの内容を取得**
- ファイル: `/path/to/weekly_sales_report.csv`

#### 4. 株価データ取得
**HTTP**アクションを3回追加（各銘柄用）:

**HTTP - Nikkei 225**
```
方法: GET
URI: https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=^N225&apikey=[YOUR_API_KEY]
ヘッダー:
  Content-Type: application/json
```

**HTTP - S&P 500**
```
方法: GET  
URI: https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=^GSPC&apikey=[YOUR_API_KEY]
ヘッダー:
  Content-Type: application/json
```

**HTTP - Recruit Holdings**
```
方法: GET
URI: https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=6098.T&apikey=[YOUR_API_KEY]
ヘッダー:
  Content-Type: application/json
```

#### 5. ニュースデータ取得
各キーワードに対して**HTTP**アクション:

**HTTP - OpenAI News**
```
方法: GET
URI: https://newsapi.org/v2/everything?q=OpenAI&apiKey=[YOUR_API_KEY]&sortBy=publishedAt&pageSize=5
```

同様にGemini, Anthropic, ElevenLabs, Perplexity, Grok, Lovableに対してもアクションを追加

#### 6. Outlookスケジュール取得
**Office 365 Outlook** → **予定表イベントの取得 (V2)**
```
予定表ID: Calendar
開始時刻: 現在の週の月曜日 00:00
終了時刻: 現在の週の日曜日 23:59
```

### Phase 3: データ処理とレポート生成

#### 7. データ処理
**作成** → **データ操作** → **作成**
JSONペイロードでデータを整理:

```json
{
  "sales_data": "[売上CSVの内容]",
  "stock_data": {
    "N225": "[株価APIレスポンス]",
    "GSPC": "[株価APIレスポンス]", 
    "6098T": "[株価APIレスポンス]"
  },
  "news_data": "[ニュースAPIレスポンス]",
  "schedule_data": "[Outlookスケジュール]"
}
```

#### 8. Google Docs作成
**HTTP** → **Google Docs API**経由でドキュメント作成

```
方法: POST
URI: https://docs.googleapis.com/v1/documents
ヘッダー:
  Authorization: Bearer [GOOGLE_ACCESS_TOKEN]
  Content-Type: application/json
本文:
{
  "title": "週次レポート - @{variables('CurrentDate')}"
}
```

#### 9. コンテンツ挿入
**HTTP** → **Google Docs API**でコンテンツ挿入:

```
方法: POST  
URI: https://docs.googleapis.com/v1/documents/[DOCUMENT_ID]:batchUpdate
本文: 
{
  "requests": [
    {
      "insertText": {
        "location": {"index": 1},
        "text": "[生成されたレポート内容]"
      }
    }
  ]
}
```

### Phase 4: 承認フロー

#### 10. Teams Adaptive Card送信
**Microsoft Teams** → **チャットまたはチャネルでメッセージを投稿**
```
投稿者: フロー ボット
投稿先: チャット（個人）
受信者: [JunyaのChat ID]
メッセージ: [Adaptive Card JSON - templates/teams-adaptive-card.json参照]
```

#### 11. 承認待機
**Microsoft Teams** → **Teams でフロー ボットの応答を待機**

### Phase 5: 最終配信

#### 12. 条件分岐
**条件**アクション:
```
条件: body('Teams_でフロー_ボットの応答を待機')?['data']?['action']
等しい: approve
```

**はいの場合**:
#### 13. 最終Teams投稿
**Microsoft Teams** → **チャットまたはチャネルでメッセージを投稿**
```
受信者: [JunyaのChat ID]  
メッセージ: 週次レポートが作成されました！
[Google Docsリンク]
```

## エラーハンドリング

### 各HTTPアクション後に条件チェック追加:
```
条件: outputs('[アクション名]')['statusCode']
等しい: 200
```

**いいえの場合**:
- **Teams通知** → エラー内容を送信
- **フローの停止** → 失敗として終了

## テスト手順

### 1. 手動テスト
1. **フローチェッカー**でエラーチェック
2. **手動テスト**実行
3. 各ステップの出力確認

### 2. スケジュールテスト
1. 短期間（1分後）にスケジュール設定
2. 全体フロー動作確認
3. 本番スケジュール（月曜8時）に変更

## 本番運用チェックリスト

- [ ] 全APIキーが正しく設定されている
- [ ] Teams Chat IDが正しく設定されている  
- [ ] Google Docs APIの認証が有効
- [ ] OneDriveのファイルパスが正しい
- [ ] スケジュール設定が正しい（月曜8:00 JST）
- [ ] エラー通知が設定されている
- [ ] 手動テストが成功している

## トラブルシューティング

### よくある問題
1. **APIレート制限**: 各API呼び出し間に遅延追加
2. **認証エラー**: コネクタの再認証
3. **JSON解析エラー**: データ形式の確認
4. **タイムアウト**: フロー設定でタイムアウト時間延長

### サポート連絡先
- Power Automate: Microsoft サポート
- API関連: 各プロバイダーのサポート
- プロジェクト関連: プロジェクトオーナー 