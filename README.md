# 週次ビジネスレポート自動生成システム

Power Automateを活用した自動化により、毎週月曜08:00に包括的なビジネスレポートを生成・配信するシステムです。

## 🎯 プロジェクト概要

### 目的
- **売上データ**、**株価情報**、**業界ニュース**、**スケジュール**を統合した週次レポートの自動生成
- Power Automateによる完全自動化フロー
- Microsoft Teams経由での承認・配信プロセス

### 最終ゴール
1. **データ収集・処理** → Pythonスクリプトによる自動実行
2. **レポート生成** → Google Docsへの自動出力
3. **承認フロー** → Teamsでの承認プロセス
4. **配信** → Junyaのプライベートチャットに自動送信

## 🏗️ システム構成

```
weeklybrief/
├── 📁 scripts/           # データ処理・レポート生成スクリプト
├── 📁 web/              # モダンなWebページ版レポート
├── 📁 power-automate/   # Power Automateフロー設計
├── 📁 templates/        # レポートテンプレート
├── 📁 config/           # 設定ファイル
├── 📁 reports/          # 生成されたレポート
├── 📁 docs/             # ドキュメント・ガイド
└── 📁 tests/            # テストデータ・サンプル
```

## 🚀 主要機能

### ✅ 実装済み機能

#### 1. データ処理システム
- **売上データ解析** (`scripts/data-processing.py`)
  - CSV形式の売上データ読み込み
  - 前年同期比・前週比計算
  - サービス別実績分析

- **株価データ取得** 
  - Alpha Vantage API連携
  - Yahoo Finance APIフォールバック
  - 日経平均、S&P 500、リクルートHD株価監視

- **ニュース収集**
  - NewsAPI + GNews API統合
  - 過去1週間のAI業界ニュース自動取得
  - 重複記事除去・日本語要約生成

#### 2. レポート生成
- **Markdownレポート** (`templates/google-docs-template.md`)
  - 構造化されたビジネス実績表示
  - HTMLテーブル形式の株価情報
  - カテゴリ別ニュース分類

- **Webページ版** (`web/`)
  - レスポンシブ・モダンUI
  - ダークモード対応
  - インタラクティブフィルタリング
  - 1画面内完結レイアウト

#### 3. 自動化基盤
- **設定管理** (`config/settings.json`)
  - APIキー一元管理
  - データソース設定
- **テスト環境** 
  - 18件のテストレポート生成実績
  - エラーハンドリング実装

### 🔄 進行中・未実装機能

#### Power Automate統合
- [ ] Teams Chat ID取得（ガイド作成済み）
- [ ] 基本フロー構築
- [ ] Google Docs API連携
- [ ] 承認フロー実装
- [ ] 自動配信設定

## 🛠️ 技術スタック

### バックエンド
- **Python 3.x**
- **ライブラリ**: pandas, requests, json, datetime
- **API**: Alpha Vantage, NewsAPI, GNews

### フロントエンド  
- **HTML5 + CSS3 + JavaScript (ES6)**
- **デザイン**: CSS Variables, Flexbox/Grid
- **アニメーション**: Intersection Observer, CSS Transitions
- **フォント**: Inter (Google Fonts)

### 自動化・統合
- **Microsoft Power Automate**
- **Google Docs API**
- **Microsoft Teams API**

## 📊 データソース

### 現在監視中のデータ
- **Placement**: 内定数 2,739件（前年同期比-6.1%、前週比+7.4%）
- **Online Platform**: 売上 ¥1.1B（前年同期比-33.2%、前週比-89.9%）
- **株価**: 日経平均¥38,486、S&P 500¥86,651、リクルートHD¥1,584
- **ニュース**: AI業界15件/週（OpenAI、Gemini、その他カテゴリ）

### API設定状況
- ✅ **Alpha Vantage**: `L5VIGOU04YJW64BT`
- ✅ **NewsAPI**: `5d88b85486d641faba9a410aca9c138b`
- ⚠️ **GNews**: 設定待ち（フリープラン利用予定）

## 🚀 使用方法

### 1. 環境セットアップ
```bash
# 仮想環境作成・有効化
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# 依存関係インストール
pip install -r requirements.txt
```

### 2. 設定ファイル更新
```bash
# APIキー設定
vim config/settings.json
```

### 3. テストレポート生成
```bash
# データ処理テスト
python scripts/test-apis.py

# レポート生成
python scripts/generate-test-report.py

# 詳細確認
python scripts/detailed-test.py
```

### 4. Webページ表示
```bash
# ローカルサーバー起動
cd web
python -m http.server 8000
# ブラウザで http://localhost:8000 にアクセス
```

## 🎨 Webページ機能

### インタラクティブ機能
- **ダークモード切り替え**: `T`キー
- **ニュースフィルタ**: `1-4`キー（全て/OpenAI/Gemini/その他）
- **エクスポート**: `E`キー（JSON形式）
- **レスポンシブデザイン**: PC・スマホ対応

### デザイン特徴
- **カード型UI**: 見やすい情報整理
- **色彩システム**: 緑（増加）・赤（減少）・黄（警告）
- **マイクロインタラクション**: ホバーエフェクト
- **1画面完結**: スクロール最小化

## 📈 実績・統計

### 開発実績
- **総ファイル数**: 28ファイル
- **総コード行数**: 2,038行
- **プロジェクトサイズ**: 28.48 KiB
- **テストレポート**: 18件生成成功

### GitHub統合
- **リポジトリ**: https://github.com/jokerjunya/weeklybrief
- **最新コミット**: a9cbf3d
- **ブランチ**: main（最新状態）

## 📋 次のステップ

### Phase 1: Power Automate基盤構築
1. **Teams Chat ID取得**
   - `scripts/teams-chat-id-helper.py`実行
   - `docs/teams-chat-id-guide.md`参照

2. **基本フロー作成**
   - `power-automate/flow-design.md`に従って構築
   - `power-automate/teams-adaptive-card.json`活用

### Phase 2: API統合・自動化
1. **Google Docs API連携**
2. **スケジュール自動実行設定**
3. **エラーハンドリング強化**

### Phase 3: 本格運用
1. **承認フロー実装**
2. **配信先設定**
3. **監視・ログ機能追加**

## 🔧 トラブルシューティング

### よくある問題
1. **APIキーエラー**: `config/settings.json`の設定確認
2. **CSVファイル読み込み**: パス設定確認（`/Users/01062544/Downloads/weekly_sales_report.csv`）
3. **ニュース取得失敗**: インターネット接続・API制限確認

### サポートドキュメント
- `docs/setup-guide.md`: 詳細セットアップ手順
- `docs/power-automate-setup.md`: Power Automate設定
- `docs/task-list.md`: 作業進捗管理

## 👥 貢献・開発

### 開発環境
- **OS**: macOS 24.3.0
- **Shell**: /bin/zsh
- **Python**: 3.x
- **IDE**: Cursor (Claude Sonnet 4 powered)

### コードスタイル
- **Python**: PEP 8準拠
- **JavaScript**: ES6+ 機能活用
- **CSS**: BEM命名規則、CSS Variables使用

---

**🎯 目標**: 完全自動化された週次ビジネスレポートシステムの構築
**📅 更新**: 2025年6月20日
**👨‍💻 開発**: Junya (GitHub: @jokerjunya) 