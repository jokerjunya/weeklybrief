# 週次レポート自動化システム

## 概要
Power Automateを使用した週次ビジネスレポート自動化システム

## 機能
- 売上データ取得（OneDrive/SharePoint）
- 株価データ取得（Alpha Vantage API）
- ニュース取得（NewsAPI）
- Outlookスケジュール取得
- Google Docsレポート生成
- Teams承認フロー
- 自動配信

## 構成
```
weeklybrief/
├── config/              # 設定ファイル
├── templates/           # テンプレート
├── power-automate/      # Power Automateフロー定義
├── scripts/             # ヘルパースクリプト
├── docs/                # ドキュメント
└── tests/               # テストデータ
```

## セットアップ手順
1. 必要なAPI キーの取得
2. Power Automate環境の準備
3. 設定ファイルの編集
4. フローのインポート

## 必要な情報
- [x] 売上データフォルダパス/ID（設定済み）
- [x] 株価ティッカーリスト（^N225, ^GSPC, 6098.T）
- [x] Google Docsレポートテンプレート（新規作成済み）
- [ ] API キー（NewsAPI, Alpha Vantage）
- [ ] Teams Chat ID（取得方法は docs/teams-chat-id-guide.md 参照）

## 現在の状況
✅ **売上データ処理**: 正常に動作（テスト済み）
✅ **HTMLテーブル生成**: 正常に動作（テスト済み）
✅ **プロジェクト基盤**: 完成
⏳ **APIキー取得**: 必要
⏳ **Teams Chat ID取得**: 必要
⏳ **Power Automateフロー構築**: 次のステップ 