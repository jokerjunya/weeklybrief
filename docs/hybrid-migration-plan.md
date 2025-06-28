# 週次ビジネスレポートシステム - ハイブリッド移行開発計画

**プロジェクト名**: AI駆動週次ビジネスレポートシステム v2.0  
**アプローチ**: ハイブリッド移行戦略  
**開発期間**: 5週間  
**開始日**: 2025年6月23日  
**完了予定**: 2025年7月25日  

---

## 🎯 プロジェクト概要

### 目標
既存の高品質資産を最大限活用しながら、理想のアーキテクチャに移行する

### 新アーキテクチャ
- **管理者サイト**: Netlifyホスト（admin-weeklyreport.netlify.app）
- **閲覧者サイト**: Netlifyホスト（weeklyreport.netlify.app）
- **Enhanced DeepResearch**: ローカルQwen3ベース深層分析システム
- **Netlify Functions**: サーバーレスAPI基盤

---

## 🔄 ハイブリッド移行戦略

### 再利用する既存資産（70%活用）

#### 🎨 **高品質フロントエンド（90%再利用）**
```
web/styles.css    → viewer-app/assets/styles.css  (そのまま移植)
web/script.js     → viewer-app/assets/script.js   (軽微調整)
web/logos/        → viewer-app/assets/logos/      (そのまま移植)
web/index.html    → viewer-app/index.html         (構造調整)
```

#### 🧠 **AI・分析基盤（70%再利用）**
```
scripts/qwen3_llm.py              → enhanced-deepresearch/reasoning_engine.py
scripts/local_llm_summarizer.py  → enhanced-deepresearch/reasoning_engine.py
scripts/company_news_collector.py → enhanced-deepresearch/data_collector.py
scripts/data-processing.py       → enhanced-deepresearch/data_manager.py
scripts/news_analyzer.py         → enhanced-deepresearch/verification_engine.py
```

### 新規開発項目（30%新規）
- 管理者Webアプリ（admin-app/）
- Enhanced DeepResearch拡張機能
- Netlify Functions API
- 管理者制御フロー

---

## 📅 詳細開発スケジュール

### **Week 1: 基盤構築 + UI移植** (6/23 - 6/29)

#### 🎯 **目標**: 新プロジェクト構造作成 + 閲覧者サイト80%完成

#### **Day 1 (6/23): プロジェクト初期化**
```bash
# 新ディレクトリ構造作成
mkdir -p {admin-app,viewer-app,enhanced-deepresearch,netlify/functions}
mkdir -p {admin-app/{assets,components},viewer-app/{assets,components}}

# 基本設定ファイル
touch {admin-app/package.json,viewer-app/package.json}
touch netlify.toml
```

#### **Day 2-3 (6/24-25): 閲覧者サイト移植**
```bash
# 既存UI資産移植
cp web/styles.css viewer-app/assets/
cp web/script.js viewer-app/assets/ 
cp -r web/logos/ viewer-app/assets/
cp web/index.html viewer-app/
```

**調整項目**:
- `index.html`: Netlify最適化
- `script.js`: API エンドポイント調整
- `styles.css`: 微調整（必要に応じて）

#### **Day 4-5 (6/26-27): 管理者サイト骨格**
```html
<!-- admin-app/index.html -->
ダッシュボード基本レイアウト作成
```

```css
/* admin-app/assets/admin.css */
管理者向けデザインシステム構築
```

#### **Week 1 成果物**
- ✅ 新プロジェクト構造完成
- ✅ 閲覧者サイト基本機能動作
- ✅ 管理者サイト骨格完成
- ✅ Netlify設定準備完了

---

### **Week 2: Enhanced DeepResearch設計 + 管理者機能** (6/30 - 7/6)

#### 🎯 **目標**: Enhanced DeepResearch基盤 + 管理者コア機能

#### **Day 1-2 (6/30-7/1): Enhanced DeepResearch 設計**

**新ファイル構造**:
```python
enhanced-deepresearch/
├── __init__.py
├── reasoning_engine.py      # Qwen3Llm拡張
├── verification_engine.py   # 信頼性検証
├── data_collector.py        # 情報収集統合
├── thinking_visualizer.py   # 思考過程可視化
├── data_manager.py          # データ処理統合
└── knowledge_graph.py       # 知識グラフ
```

**reasoning_engine.py 設計**:
```python
class EnhancedQwen3Llm(Qwen3Llm):
    """Qwen3ベース多段階推論エンジン"""
    
    def __init__(self):
        super().__init__()
        self.thinking_mode = True
        self.verification_engine = VerificationEngine()
        self.steps_log = []
    
    async def deep_research(self, topic: str) -> ResearchResult:
        """多段階深層分析"""
        # Phase 1: 問題分解
        decomposition = await self.decompose_problem(topic)
        
        # Phase 2: 反復推論
        reasoning_steps = await self.iterative_reasoning(decomposition)
        
        # Phase 3: 検証・改善
        verified_result = await self.verify_and_improve(reasoning_steps)
        
        return verified_result
```

#### **Day 3-4 (7/2-3): 管理者コア機能**

**CSV売上アップロード**:
```html
<!-- admin-app/sales-upload.html -->
<form id="salesUploadForm" enctype="multipart/form-data">
  <input type="file" accept=".csv" id="salesFile">
  <button type="submit">アップロード & 解析</button>
</form>
```

**ニュース管理インターフェース**:
```html
<!-- admin-app/news-manage.html -->
<div class="news-review-panel">
  <div class="news-item" data-news-id="123">
    <div class="priority-controls">
      <input type="range" min="0" max="10" class="priority-slider">
    </div>
  </div>
</div>
```

#### **Day 5 (7/4): イベント編集機能**
```html
<!-- admin-app/events-edit.html -->
<div class="events-editor">
  <div class="event-item">
    <input type="datetime-local" class="event-date">
    <input type="text" class="event-title" placeholder="イベントタイトル">
    <textarea class="event-description"></textarea>
  </div>
</div>
```

#### **Week 2 成果物**
- ✅ Enhanced DeepResearch基盤クラス完成
- ✅ 管理者サイトコア機能実装
- ✅ CSV アップロード機能
- ✅ ニュース優先度管理機能

---

### **Week 3: Enhanced DeepResearch実装 + API設計** (7/7 - 7/13)

#### 🎯 **目標**: DeepResearch機能実装 + Netlify Functions

#### **Day 1-3 (7/7-9): Enhanced DeepResearch実装**

**verification_engine.py**:
```python
class VerificationEngine:
    """信頼性検証エンジン"""
    
    def __init__(self, qwen3: EnhancedQwen3Llm):
        self.qwen3 = qwen3
        self.quality_threshold = 0.8
    
    async def verify_sources(self, sources: List[Source]) -> VerificationResult:
        """情報源の信頼性検証"""
        # クロスリファレンス分析
        cross_ref = await self.cross_reference_analysis(sources)
        
        # 一貫性チェック
        consistency = await self.consistency_check(sources)
        
        # 重要度スコアリング
        importance_scores = await self.calculate_importance(sources)
        
        return VerificationResult(cross_ref, consistency, importance_scores)
```

**thinking_visualizer.py**:
```python
class ThinkingVisualizer:
    """思考プロセス可視化"""
    
    def __init__(self):
        self.steps = []
        self.current_step = 0
    
    def log_thinking_step(self, step_type: str, content: str, confidence: float):
        """思考ステップ記録"""
        self.steps.append({
            'step': self.current_step,
            'type': step_type,
            'content': content,
            'confidence': confidence,
            'timestamp': datetime.now()
        })
        self.current_step += 1
    
    def generate_thinking_html(self) -> str:
        """思考過程HTML生成"""
        return self.render_thinking_timeline()
```

#### **Day 4-5 (7/10-11): Netlify Functions API**

**netlify/functions/upload-sales.js**:
```javascript
const { WeeklyReportProcessor } = require('../../enhanced-deepresearch/data_manager');

exports.handler = async (event, context) => {
  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, body: 'Method Not Allowed' };
  }
  
  try {
    const csvData = event.body;
    const processor = new WeeklyReportProcessor();
    const result = await processor.process_sales_data(csvData);
    
    return {
      statusCode: 200,
      body: JSON.stringify(result)
    };
  } catch (error) {
    return {
      statusCode: 500,
      body: JSON.stringify({ error: error.message })
    };
  }
};
```

**netlify/functions/manage-news.js**:
```javascript
const { EnhancedDeepAnalyzer } = require('../../enhanced-deepresearch/reasoning_engine');

exports.handler = async (event, context) => {
  const { action, newsData } = JSON.parse(event.body);
  
  const analyzer = new EnhancedDeepAnalyzer();
  
  switch (action) {
    case 'analyze':
      const analysis = await analyzer.deep_research(newsData);
      return { statusCode: 200, body: JSON.stringify(analysis) };
    
    case 'prioritize':
      const priorities = await analyzer.calculate_priorities(newsData);
      return { statusCode: 200, body: JSON.stringify(priorities) };
  }
};
```

#### **Week 3 成果物**
- ✅ Enhanced DeepResearch核心機能実装
- ✅ 思考過程可視化機能
- ✅ Netlify Functions API基盤
- ✅ 管理者↔️API連携完成

---

### **Week 4: 統合・UI完成 + テスト** (7/14 - 7/20)

#### 🎯 **目標**: 全機能統合 + UI/UX完成 + テスト

#### **Day 1-2 (7/14-15): UI/UX完成**

**管理者サイト最終仕上げ**:
```css
/* admin-app/assets/admin.css */
/* 既存viewer-app/styles.cssベースのデザインシステム拡張 */

:root {
  /* Admin特有の色彩 */
  --admin-primary: #6366f1;
  --admin-success: #10b981;
  --admin-warning: #f59e0b;
  --admin-danger: #ef4444;
}

.admin-dashboard {
  display: grid;
  grid-template-areas: 
    "sidebar main"
    "sidebar main";
  grid-template-columns: 250px 1fr;
  min-height: 100vh;
}

.admin-sidebar {
  grid-area: sidebar;
  background: var(--bg-primary);
  border-right: 1px solid var(--border-color);
  padding: var(--space-lg);
}

.admin-main {
  grid-area: main;
  padding: var(--space-lg);
}
```

**レスポンシブ対応**:
```css
@media (max-width: 768px) {
  .admin-dashboard {
    grid-template-areas: 
      "sidebar"
      "main";
    grid-template-columns: 1fr;
  }
  
  .admin-sidebar {
    order: 2;
  }
}
```

#### **Day 3-4 (7/16-17): データフロー統合**

**管理者→閲覧者 データフロー**:
```javascript
// admin-app/assets/admin.js
class AdminReportManager {
  async generateReport() {
    // 1. CSV売上データ処理
    const salesData = await this.processSalesData();
    
    // 2. Enhanced DeepResearch実行
    const newsAnalysis = await this.runDeepResearch();
    
    // 3. イベント情報統合
    const eventData = await this.getEventData();
    
    // 4. 最終レポート生成
    const report = await this.assembleReport(salesData, newsAnalysis, eventData);
    
    // 5. 閲覧者サイト用データ更新
    await this.publishToViewer(report);
  }
}
```

#### **Day 5 (7/18): テスト実装**

**ユニットテスト**:
```python
# tests/test_enhanced_deepresearch.py
import pytest
from enhanced_deepresearch.reasoning_engine import EnhancedQwen3Llm

class TestEnhancedDeepResearch:
    
    def setup_method(self):
        self.analyzer = EnhancedQwen3Llm()
    
    async def test_deep_research_workflow(self):
        topic = "AI業界の最新動向"
        result = await self.analyzer.deep_research(topic)
        
        assert result.confidence > 0.8
        assert len(result.thinking_steps) > 3
        assert result.verification_score > 0.7
```

**統合テスト**:
```javascript
// tests/admin-integration.test.js
describe('Admin-Viewer Integration', () => {
  test('CSV upload → Report generation → Viewer update', async () => {
    // CSV アップロード
    const uploadResult = await adminApp.uploadSalesData(mockCSV);
    expect(uploadResult.success).toBe(true);
    
    // レポート生成
    const reportResult = await adminApp.generateReport();
    expect(reportResult.status).toBe('completed');
    
    // 閲覧者サイト更新確認
    const viewerData = await viewerApp.loadReportData();
    expect(viewerData.lastUpdated).toBeRecent();
  });
});
```

#### **Week 4 成果物**
- ✅ 管理者サイトUI/UX完成
- ✅ 全データフロー統合完了
- ✅ テストスイート実装
- ✅ バグ修正・パフォーマンス最適化

---

### **Week 5: デプロイ・最終調整・ドキュメント** (7/21 - 7/25)

#### 🎯 **目標**: 本番デプロイ + 最終調整 + 運用準備

#### **Day 1 (7/21): Netlify デプロイ設定**

**netlify.toml**:
```toml
[build]
  command = "npm run build"
  functions = "netlify/functions"
  publish = "viewer-app"

[build.environment]
  NODE_VERSION = "18"

[[redirects]]
  from = "/admin/*"
  to = "/admin/index.html"
  status = 200

[[redirects]]
  from = "/api/*"
  to = "/.netlify/functions/:splat"
  status = 200

[context.production.environment]
  ADMIN_SITE_URL = "https://admin-weeklyreport.netlify.app"
  VIEWER_SITE_URL = "https://weeklyreport.netlify.app"
```

**デプロイスクリプト**:
```bash
#!/bin/bash
# scripts/deploy.sh

# 管理者サイト デプロイ
cd admin-app
netlify deploy --prod --dir .

# 閲覧者サイト デプロイ  
cd ../viewer-app
netlify deploy --prod --dir .

# Enhanced DeepResearch設定
cd ../enhanced-deepresearch
python setup.py install
```

#### **Day 2-3 (7/22-23): 最終調整・最適化**

**パフォーマンス最適化**:
```javascript
// viewer-app/assets/script.js
// 遅延読み込み実装
class LazyLoadManager {
  constructor() {
    this.observer = new IntersectionObserver(this.handleIntersect.bind(this));
  }
  
  observe(element) {
    this.observer.observe(element);
  }
  
  handleIntersect(entries) {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        this.loadContent(entry.target);
        this.observer.unobserve(entry.target);
      }
    });
  }
}
```

**セキュリティ強化**:
```javascript
// netlify/functions/auth-middleware.js
exports.authCheck = (requiredRole = 'admin') => {
  return async (event, context) => {
    const token = event.headers.authorization;
    
    if (!token) {
      return { statusCode: 401, body: 'Unauthorized' };
    }
    
    // JWT検証ロジック
    const user = await verifyToken(token);
    if (user.role !== requiredRole) {
      return { statusCode: 403, body: 'Forbidden' };
    }
    
    return { user };
  };
};
```

#### **Day 4 (7/24): ドキュメント作成**

**運用マニュアル**:
```markdown
# docs/operation-manual.md

## 管理者操作手順

### 1. 売上データ更新
1. 管理者サイトにログイン
2. "売上データ"タブ選択
3. CSVファイルアップロード
4. 自動解析結果確認

### 2. ニュース査読・優先度設定
1. "ニュース管理"タブ選択
2. Enhanced DeepResearch結果確認
3. 優先度スライダー調整
4. 表示/非表示切り替え

### 3. レポート生成・公開
1. "レポート生成"タブ選択
2. プレビュー確認
3. "公開"ボタンクリック
4. 閲覧者サイト自動更新
```

**技術ドキュメント**:
```markdown
# docs/technical-architecture.md

## システム構成図
## API仕様
## データベーススキーマ
## デプロイメント手順
## トラブルシューティング
```

#### **Day 5 (7/25): 最終テスト・リリース**

**本番環境最終テスト**:
```bash
# 全機能統合テスト
npm run test:integration

# パフォーマンステスト
npm run test:performance

# セキュリティテスト
npm run test:security
```

#### **Week 5 成果物**
- ✅ 本番環境デプロイ完了
- ✅ 運用マニュアル完成
- ✅ 技術ドキュメント完成
- ✅ 最終品質保証完了

---

## 🏗️ 技術仕様詳細

### フロントエンド技術スタック
```
📱 管理者サイト
├── HTML5 + CSS3 (既存styles.css拡張)
├── Vanilla JavaScript ES6+
├── Intersection Observer API
├── File API (CSV アップロード)
└── Fetch API (Netlify Functions連携)

👀 閲覧者サイト  
├── 既存UI資産 (90%そのまま活用)
├── WeeklyReportApp クラス
├── テーマ管理システム
├── レスポンシブデザイン
└── PWA対応 (将来拡張)
```

### バックエンド技術スタック
```
🔬 Enhanced DeepResearch
├── Python 3.9+
├── Qwen3:30b (Ollama)
├── asyncio (非同期処理)
├── numpy, pandas (データ分析)
└── Beautiful Soup (Webスクレイピング)

⚡ Netlify Functions
├── Node.js 18
├── Express.js風 ハンドラー
├── JWT認証
└── CORS設定
```

### データ管理
```
💾 ストレージ戦略
├── GitHub Repository (設定・テンプレート)
├── Netlify Edge (キャッシュ)
├── JSON Files (レポートデータ)
└── Local Cache (DeepResearch結果)
```

---

## 🎯 成果物・納期

### 主要成果物
1. **管理者Webアプリ** (admin-weeklyreport.netlify.app)
2. **閲覧者Webアプリ** (weeklyreport.netlify.app)  
3. **Enhanced DeepResearch System** (ローカル実行)
4. **Netlify Functions API** (サーバーレス)
5. **運用マニュアル・技術ドキュメント**

### 品質基準
- **UI/UX**: 既存の高品質デザイン維持・向上
- **パフォーマンス**: ページ読み込み < 3秒
- **レスポンシブ**: モバイル完全対応
- **アクセシビリティ**: WCAG 2.1 AA準拠
- **セキュリティ**: JWT認証、HTTPS強制

### 納期コミット
- **Week 1-2**: 基盤完成 (7/6まで)
- **Week 3-4**: 機能完成 (7/20まで)  
- **Week 5**: 本番リリース (7/25まで)

---

## ⚠️ リスク管理

### 技術リスク
| リスク | 確率 | 影響 | 対策 |
|--------|------|------|------|
| Qwen3性能不足 | 低 | 中 | フォールバック実装 |
| Netlify制限 | 中 | 低 | 代替クラウド準備 |
| UI移植問題 | 低 | 低 | 段階的移植 |

### スケジュールリスク  
| リスク | 確率 | 影響 | 対策 |
|--------|------|------|------|
| DeepResearch開発遅延 | 中 | 高 | MVP優先実装 |
| 統合テスト問題 | 中 | 中 | 早期統合テスト |
| UI調整時間超過 | 低 | 低 | 既存資産活用 |

### 緩和策
- **週次レビュー**: 毎週金曜 進捗確認
- **MVP優先**: 核心機能優先実装
- **段階的リリース**: フェーズ別公開

---

## 🚀 プロジェクト成功の鍵

### ハイブリッドアプローチの優位性
1. **既存資産活用**: 70%のコード再利用で開発効率最大化
2. **リスク分散**: 段階的移行でリスク最小化  
3. **品質保証**: 実証済みUI/UXで高品質確保
4. **迅速なリリース**: 5週間での本格システム完成

### 期待される効果
- **開発効率**: 従来比 45%短縮
- **品質向上**: 既存UI/UX資産で高品質維持
- **運用効率**: 管理者制御型で柔軟な運用
- **拡張性**: モジュラー設計で将来拡張容易

---

**📅 開始準備完了 - 2025年6月23日より開発開始** 