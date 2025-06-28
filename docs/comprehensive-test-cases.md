# 週次ビジネスレポートシステム - 包括的テストケース設計

## A. ファイル構造・設定テスト
### A1. 必須ファイル存在確認
- [ ] admin-app/index.html
- [ ] admin-app/assets/admin.css
- [ ] admin-app/assets/admin.js
- [ ] admin-app/assets/integration-test.js
- [ ] admin-app/assets/environment.js
- [ ] viewer-app/index.html
- [ ] viewer-app/assets/styles.css
- [ ] viewer-app/assets/script.js
- [ ] enhanced-deepresearch/admin_integration.py
- [ ] enhanced-deepresearch/reasoning_engine.py
- [ ] netlify/functions/generate-report.js
- [ ] config/settings.json

### A2. 設定ファイル整合性
- [ ] config/settings.json が存在し、正しい形式
- [ ] config/target_companies.yaml が存在
- [ ] package.json（admin-app, viewer-app, netlify）の依存関係
- [ ] netlify.toml の設定

## B. 管理者サイト機能テスト
### B1. 基本UI表示
- [ ] http://localhost:9000 でアクセス可能
- [ ] サイドバーナビゲーション表示
- [ ] 5つのメインセクション（売上、ニュース、イベント、レポート、テスト）
- [ ] CSS/JSファイル正常読み込み

### B2. 売上データ管理
- [ ] CSVファイルアップロード機能
- [ ] データ検証・解析機能
- [ ] 売上分析結果表示

### B3. ニュース管理
- [ ] ニュース収集機能
- [ ] 承認・却下機能
- [ ] 優先度設定機能
- [ ] プレビュー機能

### B4. イベント管理
- [ ] 今週のイベント編集
- [ ] 保存・更新機能

### B5. レポート生成
- [ ] 統合レポート生成
- [ ] プレビュー機能
- [ ] 公開機能

## C. 閲覧者サイト機能テスト
### C1. 基本表示
- [ ] http://localhost:8001 でアクセス可能
- [ ] レポート内容表示
- [ ] レスポンシブデザイン

### C2. インタラクティブ機能
- [ ] 株価更新機能
- [ ] ニュースフィルタリング
- [ ] ナビゲーション

## D. Enhanced DeepResearch機能テスト
### D1. APIサーバー
- [ ] enhanced-deepresearch/admin_integration.py 起動
- [ ] ポート5555で稼働（5000はAirPlay Receiverが使用中）
- [ ] モジュールインポート正常

### D2. 分析エンジン
- [ ] EnhancedQwen3Llm 推論機能
- [ ] VerificationEngine 検証機能
- [ ] ThinkingVisualizer 可視化機能

### D3. API連携
- [ ] /api/deepresearch/analyze エンドポイント
- [ ] /api/news/collect エンドポイント
- [ ] /api/reports/generate エンドポイント

## E. Netlify Functions テスト
### E1. Functions存在確認
- [ ] netlify/functions/generate-report.js
- [ ] netlify/functions/manage-news.js
- [ ] netlify/functions/upload-sales.js
- [ ] netlify/functions/deepresearch-api.js

### E2. Functions機能
- [ ] CSVアップロード処理
- [ ] ニュース管理処理
- [ ] レポート生成処理
- [ ] DeepResearch API プロキシ

## F. データフロー統合テスト
### F1. 完全ワークフロー
1. [ ] 管理者：売上CSVアップロード
2. [ ] システム：ニュース自動収集
3. [ ] 管理者：ニュース承認・優先度設定
4. [ ] 管理者：イベント編集
5. [ ] システム：統合レポート生成
6. [ ] 閲覧者：レポート閲覧
7. [ ] 閲覧者：株価更新

### F2. エラーハンドリング
- [ ] 不正CSVファイル処理
- [ ] ネットワークエラー処理
- [ ] APIエラー処理
- [ ] ファイル読み込みエラー処理

## G. パフォーマンス・セキュリティテスト
### G1. パフォーマンス
- [ ] ページ読み込み速度（3秒以内）
- [ ] API レスポンス時間（5秒以内）
- [ ] 大容量CSVファイル処理

### G2. セキュリティ
- [ ] XSS対策
- [ ] CSRF対策
- [ ] ファイルアップロード制限 