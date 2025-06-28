# 🚀 Netlifyデプロイガイド - 週次ビジネスレポートシステム

## 📋 デプロイ概要

本システムは **モノレポ戦略** で2つの独立したNetlifyサイトを作成します：

1. **管理者サイト** (`admin-weeklyreport.netlify.app`)
2. **閲覧者サイト** (`weeklyreport.netlify.app`)

## 🎯 **Step 1: 管理者サイトのデプロイ**

### 1.1 新しいサイト作成

1. [Netlify](https://app.netlify.com) にログイン
2. **"Add new site"** → **"Import an existing project"** をクリック
3. **GitHub** を選択
4. `jokerjunya/weeklybrief` リポジトリを選択

### 1.2 ビルド設定

```yaml
# Site settings
Site name: admin-weeklyreport

# Build settings
Base directory: admin-app
Build command: echo 'Admin site ready for deployment'
Publish directory: .
Functions directory: netlify/functions
```

### 1.3 環境変数設定

**Site settings** → **Environment variables** で以下を設定：

```env
NODE_VERSION=18
NPM_VERSION=9
ADMIN_SITE_URL=https://admin-weeklyreport.netlify.app
VIEWER_SITE_URL=https://weeklyreport.netlify.app
```

### 1.4 ドメイン設定

**Site settings** → **Domain management** で：
- **Site name**: `admin-weeklyreport`
- **URL**: https://admin-weeklyreport.netlify.app

---

## 🎯 **Step 2: 閲覧者サイトのデプロイ**

### 2.1 新しいサイト作成

1. Netlify で **"Add new site"** をもう一度クリック
2. **GitHub** を選択
3. **同じリポジトリ** `jokerjunya/weeklybrief` を選択

### 2.2 ビルド設定

```yaml
# Site settings
Site name: weeklyreport

# Build settings
Base directory: viewer-app
Build command: echo 'Viewer site ready for deployment'
Publish directory: .
Functions directory: (空白)
```

### 2.3 環境変数設定

```env
NODE_VERSION=18
ADMIN_SITE_URL=https://admin-weeklyreport.netlify.app
```

### 2.4 ドメイン設定

**Site settings** → **Domain management** で：
- **Site name**: `weeklyreport`
- **URL**: https://weeklyreport.netlify.app

---

## ✅ **Step 3: デプロイ後の検証**

### 3.1 管理者サイト確認

📋 **チェックリスト:**
- [ ] https://admin-weeklyreport.netlify.app にアクセス可能
- [ ] ダッシュボードが表示される
- [ ] サイドバーナビゲーションが動作
- [ ] 5つのセクション（売上・ニュース・レポート・DeepResearch・統合テスト）が表示
- [ ] ダークモード切り替えが動作

### 3.2 閲覧者サイト確認

📋 **チェックリスト:**
- [ ] https://weeklyreport.netlify.app にアクセス可能
- [ ] 週次レポートが美しく表示される
- [ ] ダークモード切り替えが動作
- [ ] レスポンシブデザインが動作（モバイル対応）
- [ ] ニュースフィルタリングが動作

### 3.3 Functions動作確認

**管理者サイトで以下をテスト:**
- [ ] `/api/health` - ヘルスチェック
- [ ] `/api/upload-sales` - 売上データアップロード
- [ ] `/api/manage-news` - ニュース管理
- [ ] `/api/generate-report` - レポート生成

---

## 🛠️ **Step 4: トラブルシューティング**

### 4.1 よくある問題

#### **Functions が動作しない**
```bash
# 原因: package.json の依存関係不足
# 解決方法: netlify/package.json で依存関係を確認
```

#### **CORS エラー**
```bash
# 原因: netlify.toml の設定ミス
# 解決方法: Access-Control-Allow-Origin の設定確認
```

#### **パス解決エラー**
```bash
# 原因: Base directory の設定ミス
# 解決方法: admin-app/ または viewer-app/ の設定確認
```

### 4.2 デバッグ方法

1. **Netlify Functions Logs**
   - Site dashboard → Functions → View logs

2. **ブラウザ開発者ツール**
   - Console errors
   - Network requests
   - Sources debugging

3. **本番環境設定確認**
   ```javascript
   // ブラウザコンソールで実行
   console.log(window.location.hostname);
   console.log('Production mode:', window.location.hostname !== 'localhost');
   ```

---

## 🔧 **Step 5: カスタムドメイン設定（オプション）**

### 5.1 独自ドメイン使用時

```yaml
# 例: 企業ドメインを使用
管理者サイト: admin.yourcompany.com
閲覧者サイト: reports.yourcompany.com
```

### 5.2 SSL証明書

- Netlify が自動的に Let's Encrypt SSL を設定
- カスタムドメイン設定後、数分で有効化

---

## 📊 **Step 6: パフォーマンス最適化**

### 6.1 Lighthouse スコア確認

```bash
# 目標スコア
Performance: 90+
Accessibility: 95+
Best Practices: 90+
SEO: 85+
```

### 6.2 キャッシュ設定

```toml
# netlify.toml で設定済み
# CSS/JS: 1年キャッシュ
# 画像: 30日キャッシュ
# HTML: キャッシュなし（最新情報表示）
```

---

## 🎉 **Step 7: デプロイ完了後のNext Steps**

### 7.1 運用開始

1. **管理者向けトレーニング**
   - CSV アップロード方法
   - ニュース管理操作
   - レポート生成手順

2. **閲覧者向けアナウンス**
   - 新しいURL通知
   - 機能紹介
   - 使い方ガイド

### 7.2 監視・メンテナンス

1. **定期チェック項目**
   - [ ] サイト稼働状況（週1回）
   - [ ] Functions 動作確認（週1回）
   - [ ] パフォーマンス計測（月1回）

2. **アップデート手順**
   ```bash
   # 開発→本番反映
   git add .
   git commit -m "機能追加・修正内容"
   git push origin main
   # Netlify が自動デプロイ
   ```

---

## 📞 **サポート連絡先**

- **Netlify サポート**: https://docs.netlify.com/
- **プロジェクト Wiki**: https://github.com/jokerjunya/weeklybrief/wiki
- **Issues 報告**: https://github.com/jokerjunya/weeklybrief/issues

---

**🎯 目標**: 2つのサイトが正常に稼働し、完全なエンドツーエンド機能を提供
**📅 完了予定**: Week 6 Day 3
**🚀 次**: Enhanced DeepResearch の本格統合 