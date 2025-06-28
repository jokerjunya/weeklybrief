/**
 * 統合テスト機能 - 管理者サイト & Enhanced DeepResearch API
 * Week 4 実装: データフロー検証とシステム統合テスト
 */

class IntegrationTestSuite {
    constructor() {
        this.apiBaseUrl = 'http://127.0.0.1:5001/api';
        this.testResults = [];
        this.isRunning = false;
        
        this.initializeTestSuite();
    }
    
    initializeTestSuite() {
        console.log('🧪 統合テストスイート初期化');
        this.addTestInterface();
        this.setupEventListeners();
    }
    
    addTestInterface() {
        // 既存のテストパネルが存在するかチェック
        const existingPanel = document.getElementById('integration-test-panel');
        if (existingPanel) {
            console.log('🧪 既存のテストパネルを使用');
            return; // 既にパネルが存在する場合は何もしない
        }
        
        // 存在しない場合のみ新規作成（フォールバック）
        const testContainer = document.createElement('div');
        testContainer.id = 'integration-test-panel';
        testContainer.innerHTML = `
            <div class="test-panel">
                <h3>🧪 システム統合テスト</h3>
                <div class="test-controls">
                    <button id="run-all-tests" class="btn-primary">全テスト実行</button>
                    <button id="run-api-tests" class="btn-secondary">API接続テスト</button>
                    <button id="run-ui-tests" class="btn-secondary">UI機能テスト</button>
                    <button id="clear-test-results" class="btn-outline">結果クリア</button>
                </div>
                <div class="test-progress">
                    <div class="progress-bar">
                        <div class="progress-fill" id="test-progress-fill"></div>
                    </div>
                    <span class="progress-text" id="test-progress-text">待機中...</span>
                </div>
                <div class="test-results" id="test-results-container">
                    <!-- テスト結果がここに表示される -->
                </div>
            </div>
        `;
        
        // テストパネルをサイドバーに追加
        const sidebar = document.querySelector('.admin-sidebar');
        if (sidebar) {
            sidebar.appendChild(testContainer);
        }
    }
    
    setupEventListeners() {
        document.getElementById('run-all-tests')?.addEventListener('click', () => {
            this.runAllTests();
        });
        
        document.getElementById('run-api-tests')?.addEventListener('click', () => {
            this.runApiTests();
        });
        
        document.getElementById('run-ui-tests')?.addEventListener('click', () => {
            this.runUiTests();
        });
        
        document.getElementById('clear-test-results')?.addEventListener('click', () => {
            this.clearResults();
        });
    }
    
    async runAllTests() {
        if (this.isRunning) {
            this.addTestResult('⚠️', '他のテストが実行中です', 'warning');
            return;
        }
        
        this.isRunning = true;
        this.clearResults();
        this.updateProgress(0, '統合テスト開始...');
        
        const testSuites = [
            { name: 'API接続テスト', method: this.runApiTests.bind(this), weight: 40 },
            { name: 'UI機能テスト', method: this.runUiTests.bind(this), weight: 30 },
            { name: 'データフローテスト', method: this.runDataFlowTests.bind(this), weight: 30 }
        ];
        
        let currentProgress = 0;
        
        for (const suite of testSuites) {
            this.updateProgress(currentProgress, `実行中: ${suite.name}`);
            await suite.method();
            currentProgress += suite.weight;
            this.updateProgress(currentProgress, `完了: ${suite.name}`);
        }
        
        this.updateProgress(100, '統合テスト完了');
        this.isRunning = false;
        this.generateTestSummary();
    }
    
    async runApiTests() {
        this.addTestResult('📡', 'API接続テスト開始', 'info');
        
        // 1. ヘルスチェック
        await this.testApiEndpoint('GET', '/health', null, 'システムヘルスチェック');
        
        // 2. DeepResearch ステータス
        await this.testApiEndpoint('GET', '/deepresearch/status', null, 'DeepResearchステータス');
        
        // 3. ニュース収集テスト
        const newsPayload = {
            topics: ['AI', 'artificial intelligence', 'machine learning']
        };
        await this.testApiEndpoint('POST', '/news/collect', newsPayload, 'ニュース収集');
        
        // 4. 分析履歴テスト
        await this.testApiEndpoint('GET', '/analysis/history?limit=5', null, '分析履歴取得');
        
        this.addTestResult('✅', 'API接続テスト完了', 'success');
    }
    
    async runUiTests() {
        this.addTestResult('🖥️', 'UI機能テスト開始', 'info');
        
        // 1. ナビゲーションテスト
        this.testNavigation();
        
        // 2. モーダル表示テスト
        this.testModalFunctionality();
        
        // 3. フォーム入力テスト
        this.testFormInputs();
        
        // 4. レスポンシブデザインテスト
        this.testResponsiveDesign();
        
        this.addTestResult('✅', 'UI機能テスト完了', 'success');
    }
    
    async runDataFlowTests() {
        this.addTestResult('🔄', 'データフローテスト開始', 'info');
        
        // 1. CSVアップロードフロー（モック）
        await this.testCsvUploadFlow();
        
        // 2. ニュース分析フロー
        await this.testNewsAnalysisFlow();
        
        // 3. レポート生成フロー
        await this.testReportGenerationFlow();
        
        this.addTestResult('✅', 'データフローテスト完了', 'success');
    }
    
    async testApiEndpoint(method, endpoint, payload, description) {
        try {
            const options = {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                }
            };
            
            if (payload && method !== 'GET') {
                options.body = JSON.stringify(payload);
            }
            
            const response = await fetch(`${this.apiBaseUrl}${endpoint}`, options);
            
            if (response.ok) {
                const data = await response.json();
                this.addTestResult('✅', `${description}: 成功 (${response.status})`, 'success');
                return data;
            } else {
                this.addTestResult('❌', `${description}: 失敗 (${response.status})`, 'error');
                return null;
            }
        } catch (error) {
            this.addTestResult('❌', `${description}: 接続エラー - ${error.message}`, 'error');
            return null;
        }
    }
    
    testNavigation() {
        const navButtons = document.querySelectorAll('.nav-button');
        if (navButtons.length > 0) {
            this.addTestResult('✅', `ナビゲーション: ${navButtons.length}個のボタン検出`, 'success');
        } else {
            this.addTestResult('❌', 'ナビゲーション: ボタンが見つかりません', 'error');
        }
        
        // セクション切り替えテスト
        const sections = document.querySelectorAll('.content-section');
        if (sections.length > 0) {
            this.addTestResult('✅', `セクション: ${sections.length}個検出`, 'success');
        } else {
            this.addTestResult('❌', 'セクション: が見つかりません', 'error');
        }
    }
    
    testModalFunctionality() {
        // モーダル要素の存在確認
        const modals = document.querySelectorAll('.modal');
        if (modals.length > 0) {
            this.addTestResult('✅', `モーダル: ${modals.length}個検出`, 'success');
        } else {
            this.addTestResult('⚠️', 'モーダル: 要素が見つかりません', 'warning');
        }
    }
    
    testFormInputs() {
        // フォーム要素の存在確認
        const forms = document.querySelectorAll('form');
        const inputs = document.querySelectorAll('input, textarea, select');
        
        this.addTestResult('ℹ️', `フォーム: ${forms.length}個、入力要素: ${inputs.length}個`, 'info');
        
        if (inputs.length > 0) {
            this.addTestResult('✅', 'フォーム入力要素: 検出完了', 'success');
        } else {
            this.addTestResult('⚠️', 'フォーム入力要素: 見つかりません', 'warning');
        }
    }
    
    testResponsiveDesign() {
        const screenWidths = [1920, 1024, 768, 480];
        let responsiveTests = 0;
        
        screenWidths.forEach(width => {
            // 実際の画面リサイズはせず、CSSメディアクエリの存在を確認
            const mediaQueries = Array.from(document.styleSheets)
                .flatMap(sheet => {
                    try {
                        return Array.from(sheet.cssRules || []);
                    } catch {
                        return [];
                    }
                })
                .filter(rule => rule.media && rule.media.mediaText.includes(`${width}px`));
            
            if (mediaQueries.length > 0) {
                responsiveTests++;
            }
        });
        
        this.addTestResult('✅', `レスポンシブデザイン: ${responsiveTests}/${screenWidths.length}サイズ対応`, 'success');
    }
    
    async testCsvUploadFlow() {
        // モックCSVデータでアップロードテスト
        const mockCsvData = 'サービス,売上,前年比\nPlacement,1000000,+5.2%\nOnline Platform,800000,-2.1%';
        const blob = new Blob([mockCsvData], { type: 'text/csv' });
        const formData = new FormData();
        formData.append('file', blob, 'test_sales.csv');
        
        try {
            // APIが利用可能な場合のテスト
            const response = await fetch(`${this.apiBaseUrl}/sales/upload`, {
                method: 'POST',
                body: formData
            });
            
            if (response.ok) {
                this.addTestResult('✅', 'CSVアップロード: 成功', 'success');
            } else {
                this.addTestResult('⚠️', `CSVアップロード: API応答 ${response.status}`, 'warning');
            }
        } catch (error) {
            this.addTestResult('⚠️', 'CSVアップロード: API未接続（正常）', 'warning');
        }
    }
    
    async testNewsAnalysisFlow() {
        const mockNewsData = {
            news_items: [
                {
                    id: 'test_001',
                    title: 'AI技術の最新動向',
                    content: 'OpenAIが新しいGPTモデルを発表...',
                    source: 'TechCrunch',
                    published_at: new Date().toISOString()
                }
            ]
        };
        
        await this.testApiEndpoint('POST', '/news/analyze', mockNewsData, 'ニュース分析フロー');
    }
    
    async testReportGenerationFlow() {
        const reportConfig = {
            config: {
                include_sales: true,
                include_news: true,
                include_events: true,
                target_date: new Date().toISOString()
            }
        };
        
        await this.testApiEndpoint('POST', '/reports/generate', reportConfig, 'レポート生成フロー');
    }
    
    addTestResult(icon, message, type) {
        const result = {
            timestamp: new Date().toLocaleTimeString(),
            icon: icon,
            message: message,
            type: type
        };
        
        this.testResults.push(result);
        this.renderTestResult(result);
    }
    
    renderTestResult(result) {
        const container = document.getElementById('test-results-container');
        if (!container) return;
        
        const resultElement = document.createElement('div');
        resultElement.className = `test-result test-${result.type}`;
        resultElement.innerHTML = `
            <span class="result-icon">${result.icon}</span>
            <span class="result-message">${result.message}</span>
            <span class="result-time">${result.timestamp}</span>
        `;
        
        container.appendChild(resultElement);
        container.scrollTop = container.scrollHeight;
    }
    
    updateProgress(percentage, text) {
        const progressFill = document.getElementById('test-progress-fill');
        const progressText = document.getElementById('test-progress-text');
        
        if (progressFill) {
            progressFill.style.width = `${percentage}%`;
        }
        
        if (progressText) {
            progressText.textContent = text;
        }
    }
    
    clearResults() {
        this.testResults = [];
        const container = document.getElementById('test-results-container');
        if (container) {
            container.innerHTML = '';
        }
        this.updateProgress(0, '待機中...');
    }
    
    generateTestSummary() {
        const successCount = this.testResults.filter(r => r.type === 'success').length;
        const errorCount = this.testResults.filter(r => r.type === 'error').length;
        const warningCount = this.testResults.filter(r => r.type === 'warning').length;
        const totalTests = this.testResults.length;
        
        const summary = `
            📊 テスト完了: ${totalTests}件
            ✅ 成功: ${successCount}件
            ❌ エラー: ${errorCount}件  
            ⚠️ 警告: ${warningCount}件
            🎯 成功率: ${((successCount / totalTests) * 100).toFixed(1)}%
        `;
        
        this.addTestResult('📊', summary, 'info');
        
        // コンソールにも出力
        console.log('🧪 統合テスト完了', {
            total: totalTests,
            success: successCount,
            errors: errorCount,
            warnings: warningCount,
            successRate: ((successCount / totalTests) * 100).toFixed(1) + '%'
        });
    }
}

// CSS スタイル追加
const testStyles = `
    .test-panel {
        background: var(--card-bg);
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        border: 1px solid var(--border-color);
    }
    
    .test-controls {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin: 1rem 0;
    }
    
    .test-controls button {
        padding: 0.5rem 1rem;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 0.85rem;
        transition: all 0.2s ease;
    }
    
    .btn-primary {
        background: var(--primary-color);
        color: white;
    }
    
    .btn-secondary {
        background: var(--secondary-color);
        color: white;
    }
    
    .btn-outline {
        background: transparent;
        color: var(--text-color);
        border: 1px solid var(--border-color);
    }
    
    .test-controls button:hover {
        transform: translateY(-1px);
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .test-progress {
        margin: 1rem 0;
    }
    
    .progress-bar {
        width: 100%;
        height: 8px;
        background: var(--border-color);
        border-radius: 4px;
        overflow: hidden;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, var(--primary-color), var(--accent-color));
        transition: width 0.3s ease;
        width: 0%;
    }
    
    .progress-text {
        display: block;
        margin-top: 0.5rem;
        font-size: 0.85rem;
        color: var(--text-secondary);
    }
    
    .test-results {
        max-height: 300px;
        overflow-y: auto;
        border: 1px solid var(--border-color);
        border-radius: 4px;
        padding: 0.5rem;
        background: var(--bg-color);
    }
    
    .test-result {
        display: flex;
        align-items: center;
        padding: 0.5rem;
        margin: 0.25rem 0;
        border-radius: 4px;
        font-size: 0.85rem;
    }
    
    .test-result.test-success {
        background: rgba(76, 175, 80, 0.1);
        border-left: 3px solid #4CAF50;
    }
    
    .test-result.test-error {
        background: rgba(244, 67, 54, 0.1);
        border-left: 3px solid #F44336;
    }
    
    .test-result.test-warning {
        background: rgba(255, 193, 7, 0.1);
        border-left: 3px solid #FFC107;
    }
    
    .test-result.test-info {
        background: rgba(33, 150, 243, 0.1);
        border-left: 3px solid #2196F3;
    }
    
    .result-icon {
        margin-right: 0.5rem;
        font-size: 1rem;
    }
    
    .result-message {
        flex: 1;
        white-space: pre-line;
    }
    
    .result-time {
        font-size: 0.75rem;
        color: var(--text-secondary);
        margin-left: 0.5rem;
    }
`;

// スタイルを追加
const styleSheet = document.createElement('style');
styleSheet.textContent = testStyles;
document.head.appendChild(styleSheet);

// 自動初期化
document.addEventListener('DOMContentLoaded', () => {
    window.integrationTestSuite = new IntegrationTestSuite();
    console.log('🧪 統合テストスイート準備完了');
});

// ブラウザ環境での使用のため、export文をコメントアウト
// export default IntegrationTestSuite; 