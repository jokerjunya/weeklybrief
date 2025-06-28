# 📊 週次ビジネスレポートシステム

**高度なAI分析機能を備えた企業向け週次レポート自動生成・管理システム**

## 🌟 システム概要

本システムは、売上データ分析、AI業界ニュース分析、株価データ収集を統合し、経営陣向けの週次レポートを自動生成するWebアプリケーションです。

### 主要機能

- 📈 **売上データ分析**: CSV アップロードによる自動分析
- 🤖 **Enhanced DeepResearch**: Qwen3:30b ベースの高度AI分析
- 📰 **ニュース管理**: AI業界ニュースの収集・優先度付け
- 📊 **レポート生成**: 美しいHTML/PDF レポート自動生成
- 👥 **デュアルサイト**: 管理者用・閲覧者用の分離設計

## 🏗️ アーキテクチャ

### サイト構成（Netlify モノレポ戦略）
```
📦 weeklybrief/
├── 🔧 admin-app/          # 管理者サイト (admin-weeklyreport.netlify.app)
├── 👁️ viewer-app/         # 閲覧者サイト (weeklyreport.netlify.app)
├── 🚀 netlify/functions/  # サーバーレス関数
├── 🧠 enhanced-deepresearch/ # AI分析エンジン
└── ⚙️ config/            # 設定ファイル
```

### 技術スタック

**フロントエンド**
- HTML5, CSS3, Vanilla JavaScript
- D3.js (データビジュアライゼーション)
- Chart.js (グラフ描画)
- レスポンシブデザイン

**バックエンド**
- Netlify Functions (Node.js)
- Python Flask (AI分析エンジン)
- SQLite (データ保存)

**AI・分析**
- Qwen3:30b (ローカルLLM)
- 多段階推論エンジン
- 信頼性検証システム
- 思考プロセス可視化

## 🚀 デプロイ手順

### 1. 必要な準備

```bash
# リポジトリクローン
git clone https://github.com/your-username/weeklybrief.git
cd weeklybrief

# 依存関係インストール
pip install -r requirements.txt
```

### 2. Netlify デプロイ

#### 管理者サイト (admin-weeklyreport.netlify.app)
1. Netlify にログイン
2. "New site from Git" を選択
3. リポジトリを選択
4. ビルド設定:
   - **Base directory**: `admin-app`
   - **Build command**: `echo 'Admin site ready'`
   - **Publish directory**: `.`
   - **Functions directory**: `netlify/functions`

#### 閲覧者サイト (weeklyreport.netlify.app)
1. Netlify で新しいサイトを作成
2. ビルド設定:
   - **Base directory**: `viewer-app`
   - **Build command**: `echo 'Viewer site ready'`
   - **Publish directory**: `.`

### 3. 環境変数設定

Netlify の Environment Variables で設定:

```env
# 管理者サイト用
ADMIN_SITE_URL=https://admin-weeklyreport.netlify.app
VIEWER_SITE_URL=https://weeklyreport.netlify.app
NODE_VERSION=18

# AI分析用 (オプション)
QWEN3_MODEL_PATH=/path/to/qwen3/model
OPENAI_API_KEY=your_openai_key_here
```

## 💻 ローカル開発

### サーバー起動

```bash
# 管理者サイト (ポート 8000)
cd admin-app && python -m http.server 8000

# 閲覧者サイト (ポート 8003)
cd viewer-app && python -m http.server 8003

# AI分析エンジン (ポート 5001)
cd enhanced-deepresearch && python simple_api_server.py
```

### アクセスURL
- 管理者サイト: http://localhost:8000
- 閲覧者サイト: http://localhost:8003
- API サーバー: http://localhost:5001/api

## 📋 使用方法

### 管理者向け

1. **売上データアップロード**
   - CSV ファイルをドラッグ&ドロップ
   - 自動分析・グラフ生成

2. **ニュース管理**
   - AI業界ニュース自動収集
   - 優先度・表示可否の設定

3. **レポート生成**
   - ワンクリックでHTML/PDF生成
   - プレビュー・公開機能

### 閲覧者向け

1. **レポート閲覧**
   - 美しいレスポンシブUI
   - ダークモード対応

2. **データ更新**
   - 株価情報のリアルタイム更新
   - エクスポート機能

## 🧠 Enhanced DeepResearch

### 機能

- **多段階推論**: 複雑な分析を4段階で実行
- **信頼性検証**: 複数ソースのクロスリファレンス
- **思考可視化**: D3.js によるインタラクティブ図
- **品質評価**: 自動的な品質メトリクス計算

### AI分析プロセス

```
📊 データ収集 → 🔍 分析 → ✅ 検証 → 📈 統合 → 📄 レポート生成
```

## 📊 コード統計

- **総行数**: 約8,000行
- **Python**: 3,406行 (Enhanced DeepResearch)
- **JavaScript**: 2,500行+ (フロントエンド)
- **HTML/CSS**: 1,747行 (UI)
- **設定ファイル**: 300行+

## 🔧 システム要件

### 本番環境
- Netlify (無料プラン対応)
- 外部API: 不要 (完全セルフホスト可能)

### ローカル開発
- Python 3.8+
- Node.js 18+
- メモリ: 4GB+ (Qwen3使用時は16GB推奨)

## 🛡️ セキュリティ

- CSP (Content Security Policy) 設定済み
- CORS 適切に制限
- 機密データの.gitignore 設定
- XSS/CSRF 対策実装

## 📈 パフォーマンス

- Lighthouse スコア: 90+
- CDN キャッシュ最適化
- 画像・CSS 最適化済み
- プリロード設定

## 🔄 今後の開発計画

- [ ] PWA 対応
- [ ] リアルタイム更新機能
- [ ] ユーザー認証システム
- [ ] コメント・共有機能
- [ ] モバイルアプリ対応

## 🤝 コントリビューション

1. フォークしてブランチ作成
2. 機能追加・バグ修正
3. テスト追加
4. プルリクエスト送信

## 📄 ライセンス

MIT License - 詳細は [LICENSE](LICENSE) ファイルを参照

## 📞 サポート

- 📧 Email: support@weeklyreport.example.com
- 📖 Wiki: [プロジェクトWiki](https://github.com/your-username/weeklybrief/wiki)
- 🐛 Issues: [GitHub Issues](https://github.com/your-username/weeklybrief/issues)

---

**作成**: 2025年6月 | **最終更新**: 2025年6月28日 