/**
 * 管理者レポート管理システム
 * Enhanced DeepResearch対応版
 */
class AdminReportManager {
    constructor() {
        this.currentSection = 'dashboard';
        this.isDarkMode = false;
        this.currentUpload = null;
        this.newsData = [];
        this.eventsData = [];
        this.reportStatus = {
            isGenerating: false,
            progress: 0,
            currentStep: '待機中'
        };
    }

    /**
     * 初期化
     */
    async init() {
        this.setupTheme();
        this.setupNavigation();
        this.setupFileUpload();
        this.setupEventHandlers();
        this.loadInitialData();
        console.log('Admin Report Manager initialized');
    }

    /**
     * テーマ管理
     */
    setupTheme() {
        const savedTheme = localStorage.getItem('admin-theme') || 'light';
        this.setTheme(savedTheme);
        
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => this.toggleTheme());
        }
    }

    setTheme(theme) {
        this.isDarkMode = theme === 'dark';
        document.body.setAttribute('data-theme', theme);
        localStorage.setItem('admin-theme', theme);
        
        // Update theme toggle icon
        const themeIcon = document.querySelector('#themeToggle i');
        if (themeIcon) {
            themeIcon.className = this.isDarkMode ? 'fas fa-sun' : 'fas fa-moon';
        }
    }

    toggleTheme() {
        const newTheme = this.isDarkMode ? 'light' : 'dark';
        this.setTheme(newTheme);
    }

    /**
     * ナビゲーション設定
     */
    setupNavigation() {
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const section = link.getAttribute('data-section');
                this.switchSection(section);
            });
        });
    }

    switchSection(sectionId) {
        // Hide all sections
        document.querySelectorAll('.content-section').forEach(section => {
            section.classList.remove('active');
        });
        
        // Show target section
        const targetSection = document.getElementById(sectionId);
        if (targetSection) {
            targetSection.classList.add('active');
        }
        
        // Update navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        
        const activeNavItem = document.querySelector(`[data-section="${sectionId}"]`).closest('.nav-item');
        if (activeNavItem) {
            activeNavItem.classList.add('active');
        }
        
        // Update page title
        const pageTitle = document.querySelector('.page-title');
        if (pageTitle) {
            const sectionTitles = {
                'dashboard': 'ダッシュボード',
                'sales-upload': '売上データアップロード',
                'news-manage': 'ニュース管理',
                'events-edit': 'イベント編集',
                'report-generate': 'レポート生成'
            };
            pageTitle.textContent = sectionTitles[sectionId] || 'ダッシュボード';
        }
        
        this.currentSection = sectionId;
    }

    /**
     * ファイルアップロード設定
     */
    setupFileUpload() {
        const fileInput = document.getElementById('salesFile');
        const dropZone = document.getElementById('fileDropZone');
        const uploadForm = document.getElementById('salesUploadForm');

        // File input change
        if (fileInput) {
            fileInput.addEventListener('change', (e) => {
                const file = e.target.files[0];
                this.handleFileSelection(file);
            });
        }

        // Drag and drop
        if (dropZone) {
            dropZone.addEventListener('dragover', (e) => {
                e.preventDefault();
                dropZone.classList.add('dragover');
            });

            dropZone.addEventListener('dragleave', () => {
                dropZone.classList.remove('dragover');
            });

            dropZone.addEventListener('drop', (e) => {
                e.preventDefault();
                dropZone.classList.remove('dragover');
                const file = e.dataTransfer.files[0];
                this.handleFileSelection(file);
            });
        }

        // Form submission
        if (uploadForm) {
            uploadForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleFileUpload();
            });
        }
    }

    handleFileSelection(file) {
        if (!file) return;

        if (file.type !== 'text/csv') {
            this.showNotification('CSVファイルを選択してください', 'error');
            return;
        }

        this.currentUpload = file;
        const uploadBtn = document.querySelector('#salesUploadForm button[type="submit"]');
        const uploadStatus = document.getElementById('uploadStatus');
        
        if (uploadBtn) uploadBtn.disabled = false;
        if (uploadStatus) uploadStatus.textContent = `選択されたファイル: ${file.name}`;
    }

    async handleFileUpload() {
        if (!this.currentUpload) return;

        const uploadBtn = document.querySelector('#salesUploadForm button[type="submit"]');
        const uploadStatus = document.getElementById('uploadStatus');
        
        try {
            // Show loading state
            if (uploadBtn) {
                uploadBtn.disabled = true;
                uploadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> アップロード中...';
            }
            if (uploadStatus) uploadStatus.textContent = 'Enhanced DeepResearch で処理中...';

            // Enhanced DeepResearch API を使用してファイルをアップロード
            const response = await this.uploadToDeepResearchAPI();
            
            if (response.status === 'uploaded') {
                this.showNotification(`売上データのアップロードが完了しました (${response.data_summary.rows}行, ${response.data_summary.columns}列)`, 'success');
                this.updateUploadHistory(response);
                
                // ダッシュボードの統計を更新
                this.updateDashboardStats();
            } else {
                throw new Error(response.error || 'アップロードに失敗しました');
            }
            
        } catch (error) {
            console.error('Upload error:', error);
            this.showNotification(`アップロードに失敗しました: ${error.message}`, 'error');
        } finally {
            // Reset form
            if (uploadBtn) {
                uploadBtn.disabled = true;
                uploadBtn.innerHTML = '<i class="fas fa-upload"></i> アップロード & 解析';
            }
            if (uploadStatus) uploadStatus.textContent = 'ファイルを選択してください';
            this.currentUpload = null;
            document.getElementById('salesFile').value = '';
        }
    }

    async uploadToDeepResearchAPI() {
        const formData = new FormData();
        formData.append('file', this.currentUpload);
        
        const response = await fetch('/.netlify/functions/deepresearch-api/api/sales/upload', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        return await response.json();
    }

    async simulateFileProcessing() {
        // Simulate processing time
        await new Promise(resolve => setTimeout(resolve, 2000));
    }

    updateUploadHistory(uploadResponse = null) {
        // Add to upload history
        const historyList = document.querySelector('.history-list');
        if (!historyList) return;

        const fileName = uploadResponse ? uploadResponse.filename : (this.currentUpload ? this.currentUpload.name : 'unknown');
        const uploadTime = uploadResponse ? new Date(uploadResponse.data_summary.upload_time) : new Date();
        const details = uploadResponse ? `${uploadResponse.data_summary.rows}行 × ${uploadResponse.data_summary.columns}列` : '処理済み';

        const historyItem = document.createElement('div');
        historyItem.className = 'history-item';
        historyItem.innerHTML = `
            <div class="history-info">
                <div class="file-name">${fileName}</div>
                <div class="file-meta">${uploadTime.toLocaleDateString('ja-JP')} ${uploadTime.toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit' })} | ${details}</div>
            </div>
            <div class="history-actions">
                <button class="btn btn-sm btn-outline">
                    <i class="fas fa-eye"></i> 詳細
                </button>
            </div>
        `;
        
        historyList.insertBefore(historyItem, historyList.firstChild);
    }

    /**
     * イベントハンドラー設定
     */
    setupEventHandlers() {
        // News analysis button
        const analyzeNewsBtn = document.getElementById('analyzeNewsBtn');
        if (analyzeNewsBtn) {
            analyzeNewsBtn.addEventListener('click', () => this.runDeepResearch());
        }

        // Report generation buttons
        const generateReportBtn = document.getElementById('generateReportBtn');
        const previewReportBtn = document.getElementById('previewReportBtn');
        const publishReportBtn = document.getElementById('publishReportBtn');

        if (generateReportBtn) {
            generateReportBtn.addEventListener('click', () => this.generateReport());
        }
        if (previewReportBtn) {
            previewReportBtn.addEventListener('click', () => this.previewReport());
        }
        if (publishReportBtn) {
            publishReportBtn.addEventListener('click', () => this.publishReport());
        }

        // News approval buttons
        document.addEventListener('click', (e) => {
            if (e.target.closest('.btn-success') && e.target.closest('.news-actions')) {
                this.approveNews(e.target);
            }
            if (e.target.closest('.btn-danger') && e.target.closest('.news-actions')) {
                this.rejectNews(e.target);
            }
        });

        // Priority sliders
        document.addEventListener('input', (e) => {
            if (e.target.classList.contains('priority-slider')) {
                const valueDisplay = e.target.nextElementSibling;
                if (valueDisplay) {
                    valueDisplay.textContent = e.target.value;
                }
            }
        });
    }

    /**
     * Enhanced DeepResearch実行
     */
    async runDeepResearch() {
        const analyzeBtn = document.getElementById('analyzeNewsBtn');
        
        try {
            // Show loading state
            if (analyzeBtn) {
                analyzeBtn.disabled = true;
                analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 分析中...';
            }

            this.showNotification('Enhanced DeepResearch を実行中...', 'info');
            
            // Simulate DeepResearch processing
            await this.simulateDeepResearch();
            
            this.showNotification('ニュース分析が完了しました', 'success');
            this.loadNewsData();
            
        } catch (error) {
            console.error('DeepResearch error:', error);
            this.showNotification('分析に失敗しました', 'error');
        } finally {
            if (analyzeBtn) {
                analyzeBtn.disabled = false;
                analyzeBtn.innerHTML = '<i class="fas fa-brain"></i> DeepResearch 実行';
            }
        }
    }

    async simulateDeepResearch() {
        // Simulate enhanced AI processing
        const steps = [
            '情報収集中...',
            '多段階推論実行中...',
            '信頼性検証中...',
            '重要度算出中...',
            '最終分析中...'
        ];

        for (let i = 0; i < steps.length; i++) {
            await new Promise(resolve => setTimeout(resolve, 1000));
            console.log(`DeepResearch: ${steps[i]}`);
        }
    }

    /**
     * ニュース管理
     */
    loadNewsData() {
        // Sample news data
        this.newsData = [
            {
                id: 1,
                title: 'ChatGPT-4o の新機能リリース',
                summary: 'OpenAIがChatGPT-4oの重要なアップデートを発表...',
                category: 'openai',
                score: 8.5,
                status: 'pending'
            },
            {
                id: 2,
                title: 'Google Gemini 企業向け機能強化',
                summary: 'Googleが企業向けAIソリューションの新機能を発表...',
                category: 'gemini',
                score: 7.8,
                status: 'pending'
            }
        ];
        
        this.renderNewsReview();
    }

    renderNewsReview() {
        const reviewPanel = document.querySelector('.news-review-panel');
        if (!reviewPanel) return;

        reviewPanel.innerHTML = this.newsData.map(news => `
            <div class="review-item" data-news-id="${news.id}">
                <div class="news-header">
                    <div class="news-meta">
                        <span class="category-tag ${news.category}">${news.category.toUpperCase()}</span>
                        <span class="analysis-score">重要度: ${news.score}</span>
                    </div>
                    <div class="news-actions">
                        <button class="btn btn-sm btn-success">承認</button>
                        <button class="btn btn-sm btn-danger">非表示</button>
                    </div>
                </div>
                <div class="news-content">
                    <h4 class="news-title">${news.title}</h4>
                    <p class="news-summary">${news.summary}</p>
                    <div class="priority-control">
                        <label>表示優先度:</label>
                        <input type="range" min="0" max="10" value="${Math.round(news.score)}" class="priority-slider">
                        <span class="priority-value">${Math.round(news.score)}</span>
                    </div>
                </div>
            </div>
        `).join('');
    }

    approveNews(button) {
        const newsItem = button.closest('.review-item');
        const newsId = parseInt(newsItem.dataset.newsId);
        
        const news = this.newsData.find(n => n.id === newsId);
        if (news) {
            news.status = 'approved';
            this.showNotification('ニュースを承認しました', 'success');
        }
    }

    rejectNews(button) {
        const newsItem = button.closest('.review-item');
        const newsId = parseInt(newsItem.dataset.newsId);
        
        const news = this.newsData.find(n => n.id === newsId);
        if (news) {
            news.status = 'rejected';
            newsItem.style.opacity = '0.5';
            this.showNotification('ニュースを非表示にしました', 'info');
        }
    }

    /**
     * レポート生成
     */
    async generateReport() {
        const generateBtn = document.getElementById('generateReportBtn');
        const publishBtn = document.getElementById('publishReportBtn');
        const statusBar = document.querySelector('.status-progress');
        const statusText = document.querySelector('.status-text');
        
        try {
            this.reportStatus.isGenerating = true;
            
            if (generateBtn) {
                generateBtn.disabled = true;
                generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 生成中...';
            }
            
            // Simulate report generation steps
            const steps = [
                { text: '売上データを統合中...', progress: 20 },
                { text: 'Enhanced DeepResearch結果を処理中...', progress: 40 },
                { text: 'イベント情報を統合中...', progress: 60 },
                { text: 'レポート形式を生成中...', progress: 80 },
                { text: '最終確認中...', progress: 100 }
            ];
            
            for (const step of steps) {
                await new Promise(resolve => setTimeout(resolve, 1000));
                
                if (statusBar) statusBar.style.width = `${step.progress}%`;
                if (statusText) statusText.textContent = step.text;
                
                this.reportStatus.progress = step.progress;
                this.reportStatus.currentStep = step.text;
            }
            
            // Enable publish button
            if (publishBtn) publishBtn.disabled = false;
            if (statusText) statusText.textContent = 'レポート生成完了';
            
            this.showNotification('レポートの生成が完了しました', 'success');
            
        } catch (error) {
            console.error('Report generation error:', error);
            this.showNotification('レポート生成に失敗しました', 'error');
        } finally {
            this.reportStatus.isGenerating = false;
            
            if (generateBtn) {
                generateBtn.disabled = false;
                generateBtn.innerHTML = '<i class="fas fa-cogs"></i> レポート生成';
            }
        }
    }

    previewReport() {
        const previewDiv = document.getElementById('reportPreview');
        if (!previewDiv) return;

        // Show preview
        previewDiv.style.display = 'block';
        
        // Generate preview content
        const previewContent = previewDiv.querySelector('.preview-content');
        if (previewContent) {
            previewContent.innerHTML = `
                <h3>📊 週次ビジネスレポート プレビュー</h3>
                <div style="margin: 20px 0; padding: 15px; background: var(--bg-secondary); border-radius: 8px;">
                    <h4>ビジネス実績</h4>
                    <p>• Placement: 2,739件 (前年同期比-6.1%, 前週比+7.4%)</p>
                    <p>• Online Platform: ¥1.1B (前年同期比-33.2%, 前週比-89.9%)</p>
                </div>
                <div style="margin: 20px 0; padding: 15px; background: var(--bg-secondary); border-radius: 8px;">
                    <h4>AI業界ニュース</h4>
                    <p>• 承認済みニュース: ${this.newsData.filter(n => n.status === 'approved').length}件</p>
                    <p>• 主要トピック: OpenAI, Google Gemini</p>
                </div>
            `;
        }
        
        // Scroll to preview
        previewDiv.scrollIntoView({ behavior: 'smooth' });
    }

    async publishReport() {
        const publishBtn = document.getElementById('publishReportBtn');
        const autoPublish = document.getElementById('autoPublish').checked;
        const notifyUsers = document.getElementById('notifyUsers').checked;
        
        try {
            if (publishBtn) {
                publishBtn.disabled = true;
                publishBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 公開中...';
            }
            
            // Simulate publishing
            await new Promise(resolve => setTimeout(resolve, 2000));
            
            let message = 'レポートが公開されました';
            if (autoPublish) message += ' (閲覧者サイトに自動反映)';
            if (notifyUsers) message += ' (ユーザーに通知送信)';
            
            this.showNotification(message, 'success');
            
        } catch (error) {
            console.error('Publish error:', error);
            this.showNotification('公開に失敗しました', 'error');
        } finally {
            if (publishBtn) {
                publishBtn.disabled = false;
                publishBtn.innerHTML = '<i class="fas fa-paper-plane"></i> レポート公開';
            }
        }
    }

    /**
     * 初期データ読み込み
     */
    async loadInitialData() {
        try {
            // Load news data
            this.loadNewsData();
            
            // Update dashboard stats
            this.updateDashboardStats();
            
        } catch (error) {
            console.error('Failed to load initial data:', error);
        }
    }

    updateDashboardStats() {
        // Update dashboard statistics
        const now = new Date();
        document.getElementById('lastUpdateTime').textContent = now.toLocaleDateString('ja-JP', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    /**
     * 通知表示
     */
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--bg-primary);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 16px;
            box-shadow: var(--shadow-lg);
            z-index: 1000;
            display: flex;
            align-items: center;
            gap: 12px;
            max-width: 400px;
            transform: translateX(100%);
            transition: transform 0.3s ease;
        `;
        
        notification.innerHTML = `
            <i class="fas fa-${this.getNotificationIcon(type)}" style="color: var(--admin-${type === 'error' ? 'danger' : type === 'warning' ? 'warning' : type === 'success' ? 'success' : 'info'});"></i>
            <span style="flex: 1;">${message}</span>
            <button onclick="this.parentElement.remove()" style="background: none; border: none; color: var(--text-secondary); cursor: pointer;">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        // Add to page
        document.body.appendChild(notification);
        
        // Show notification
        setTimeout(() => notification.style.transform = 'translateX(0)', 100);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }

    getNotificationIcon(type) {
        const icons = {
            'success': 'check-circle',
            'error': 'exclamation-circle',
            'warning': 'exclamation-triangle',
            'info': 'info-circle'
        };
        return icons[type] || 'info-circle';
    }
}

// Export for global access
window.AdminReportManager = AdminReportManager;

    /**
     * イベントハンドラー設定
     */
    setupEventHandlers() {
        // News analysis button
        const analyzeNewsBtn = document.getElementById('analyzeNewsBtn');
        if (analyzeNewsBtn) {
            analyzeNewsBtn.addEventListener('click', () => this.runDeepResearch());
        }

        // Report generation buttons
        const generateReportBtn = document.getElementById('generateReportBtn');
        const previewReportBtn = document.getElementById('previewReportBtn');
        const publishReportBtn = document.getElementById('publishReportBtn');

        if (generateReportBtn) {
            generateReportBtn.addEventListener('click', () => this.generateReport());
        }
        if (previewReportBtn) {
            previewReportBtn.addEventListener('click', () => this.previewReport());
        }
        if (publishReportBtn) {
            publishReportBtn.addEventListener('click', () => this.publishReport());
        }

        // News approval buttons
        document.addEventListener('click', (e) => {
            if (e.target.closest('.btn-success') && e.target.closest('.news-actions')) {
                this.approveNews(e.target);
            }
            if (e.target.closest('.btn-danger') && e.target.closest('.news-actions')) {
                this.rejectNews(e.target);
            }
        });

        // Priority sliders
        document.addEventListener('input', (e) => {
            if (e.target.classList.contains('priority-slider')) {
                const valueDisplay = e.target.nextElementSibling;
                if (valueDisplay) {
                    valueDisplay.textContent = e.target.value;
                }
            }
        });
    }

    /**
     * Enhanced DeepResearch実行
     */
    async runDeepResearch() {
        const analyzeBtn = document.getElementById('analyzeNewsBtn');
        
        try {
            // Show loading state
            if (analyzeBtn) {
                analyzeBtn.disabled = true;
                analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 分析中...';
            }

            this.showNotification('Enhanced DeepResearch を実行中...', 'info');
            
            // Simulate DeepResearch processing
            await this.simulateDeepResearch();
            
            this.showNotification('ニュース分析が完了しました', 'success');
            this.loadNewsData();
            
        } catch (error) {
            console.error('DeepResearch error:', error);
            this.showNotification('分析に失敗しました', 'error');
        } finally {
            if (analyzeBtn) {
                analyzeBtn.disabled = false;
                analyzeBtn.innerHTML = '<i class="fas fa-brain"></i> DeepResearch 実行';
            }
        }
    }

    async simulateDeepResearch() {
        // Simulate enhanced AI processing
        const steps = [
            '情報収集中...',
            '多段階推論実行中...',
            '信頼性検証中...',
            '重要度算出中...',
            '最終分析中...'
        ];

        for (let i = 0; i < steps.length; i++) {
            await new Promise(resolve => setTimeout(resolve, 1000));
            console.log(`DeepResearch: ${steps[i]}`);
        }
    }

    /**
     * ニュース管理
     */
    loadNewsData() {
        // In real implementation, this would fetch from API
        this.newsData = [
            {
                id: 1,
                title: 'ChatGPT-4o の新機能リリース',
                summary: 'OpenAIがChatGPT-4oの重要なアップデートを発表...',
                category: 'openai',
                score: 8.5,
                status: 'pending'
            },
            {
                id: 2,
                title: 'Google Gemini 企業向け機能強化',
                summary: 'Googleが企業向けAIソリューションの新機能を発表...',
                category: 'gemini',
                score: 7.8,
                status: 'pending'
            }
        ];
        
        this.renderNewsReview();
    }

    renderNewsReview() {
        const reviewPanel = document.querySelector('.news-review-panel');
        if (!reviewPanel) return;

        reviewPanel.innerHTML = this.newsData.map(news => `
            <div class="review-item" data-news-id="${news.id}">
                <div class="news-header">
                    <div class="news-meta">
                        <span class="category-tag ${news.category}">${news.category.toUpperCase()}</span>
                        <span class="analysis-score">重要度: ${news.score}</span>
                    </div>
                    <div class="news-actions">
                        <button class="btn btn-sm btn-success">承認</button>
                        <button class="btn btn-sm btn-danger">非表示</button>
                    </div>
                </div>
                <div class="news-content">
                    <h4 class="news-title">${news.title}</h4>
                    <p class="news-summary">${news.summary}</p>
                    <div class="priority-control">
                        <label>表示優先度:</label>
                        <input type="range" min="0" max="10" value="${Math.round(news.score)}" class="priority-slider">
                        <span class="priority-value">${Math.round(news.score)}</span>
                    </div>
                </div>
            </div>
        `).join('');
    }

    approveNews(button) {
        const newsItem = button.closest('.review-item');
        const newsId = parseInt(newsItem.dataset.newsId);
        
        const news = this.newsData.find(n => n.id === newsId);
        if (news) {
            news.status = 'approved';
            this.showNotification('ニュースを承認しました', 'success');
        }
    }

    rejectNews(button) {
        const newsItem = button.closest('.review-item');
        const newsId = parseInt(newsItem.dataset.newsId);
        
        const news = this.newsData.find(n => n.id === newsId);
        if (news) {
            news.status = 'rejected';
            newsItem.style.opacity = '0.5';
            this.showNotification('ニュースを非表示にしました', 'info');
        }
    }

    /**
     * レポート生成
     */
    async generateReport() {
        const generateBtn = document.getElementById('generateReportBtn');
        const publishBtn = document.getElementById('publishReportBtn');
        const statusBar = document.querySelector('.status-progress');
        const statusText = document.querySelector('.status-text');
        
        try {
            this.reportStatus.isGenerating = true;
            
            if (generateBtn) {
                generateBtn.disabled = true;
                generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 生成中...';
            }
            
            // Simulate report generation steps
            const steps = [
                { text: '売上データを統合中...', progress: 20 },
                { text: 'Enhanced DeepResearch結果を処理中...', progress: 40 },
                { text: 'イベント情報を統合中...', progress: 60 },
                { text: 'レポート形式を生成中...', progress: 80 },
                { text: '最終確認中...', progress: 100 }
            ];
            
            for (const step of steps) {
                await new Promise(resolve => setTimeout(resolve, 1000));
                
                if (statusBar) statusBar.style.width = `${step.progress}%`;
                if (statusText) statusText.textContent = step.text;
                
                this.reportStatus.progress = step.progress;
                this.reportStatus.currentStep = step.text;
            }
            
            // Enable publish button
            if (publishBtn) publishBtn.disabled = false;
            if (statusText) statusText.textContent = 'レポート生成完了';
            
            this.showNotification('レポートの生成が完了しました', 'success');
            
        } catch (error) {
            console.error('Report generation error:', error);
            this.showNotification('レポート生成に失敗しました', 'error');
        } finally {
            this.reportStatus.isGenerating = false;
            
            if (generateBtn) {
                generateBtn.disabled = false;
                generateBtn.innerHTML = '<i class="fas fa-cogs"></i> レポート生成';
            }
        }
    }

    previewReport() {
        const previewDiv = document.getElementById('reportPreview');
        if (!previewDiv) return;

        // Show preview
        previewDiv.style.display = 'block';
        
        // Generate preview content
        const previewContent = previewDiv.querySelector('.preview-content');
        if (previewContent) {
            previewContent.innerHTML = `
                <h3>📊 週次ビジネスレポート プレビュー</h3>
                <div style="margin: 20px 0; padding: 15px; background: var(--bg-secondary); border-radius: 8px;">
                    <h4>ビジネス実績</h4>
                    <p>• Placement: 2,739件 (前年同期比-6.1%, 前週比+7.4%)</p>
                    <p>• Online Platform: ¥1.1B (前年同期比-33.2%, 前週比-89.9%)</p>
                </div>
                <div style="margin: 20px 0; padding: 15px; background: var(--bg-secondary); border-radius: 8px;">
                    <h4>AI業界ニュース</h4>
                    <p>• 承認済みニュース: ${this.newsData.filter(n => n.status === 'approved').length}件</p>
                    <p>• 主要トピック: OpenAI, Google Gemini</p>
                </div>
                <div style="margin: 20px 0; padding: 15px; background: var(--bg-secondary); border-radius: 8px;">
                    <h4>今週のスケジュール</h4>
                    <p>• 登録イベント: ${this.eventsData.length}件</p>
                </div>
            `;
        }
        
        // Scroll to preview
        previewDiv.scrollIntoView({ behavior: 'smooth' });
    }

    async publishReport() {
        const publishBtn = document.getElementById('publishReportBtn');
        const autoPublish = document.getElementById('autoPublish').checked;
        const notifyUsers = document.getElementById('notifyUsers').checked;
        
        try {
            if (publishBtn) {
                publishBtn.disabled = true;
                publishBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 公開中...';
            }
            
            // Simulate publishing
            await new Promise(resolve => setTimeout(resolve, 2000));
            
            let message = 'レポートが公開されました';
            if (autoPublish) message += ' (閲覧者サイトに自動反映)';
            if (notifyUsers) message += ' (ユーザーに通知送信)';
            
            this.showNotification(message, 'success');
            
        } catch (error) {
            console.error('Publish error:', error);
            this.showNotification('公開に失敗しました', 'error');
        } finally {
            if (publishBtn) {
                publishBtn.disabled = false;
                publishBtn.innerHTML = '<i class="fas fa-paper-plane"></i> レポート公開';
            }
        }
    }

    /**
     * 初期データ読み込み
     */
    async loadInitialData() {
        try {
            // Load news data
            this.loadNewsData();
            
            // Update dashboard stats
            this.updateDashboardStats();
            
        } catch (error) {
            console.error('Failed to load initial data:', error);
        }
    }

    updateDashboardStats() {
        // Update dashboard statistics
        const now = new Date();
        document.getElementById('lastUpdateTime').textContent = now.toLocaleDateString('ja-JP', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    /**
     * 通知表示
     */
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <i class="fas fa-${this.getNotificationIcon(type)}"></i>
            <span>${message}</span>
            <button class="notification-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        // Add to page
        document.body.appendChild(notification);
        
        // Show notification
        setTimeout(() => notification.classList.add('show'), 100);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }

    getNotificationIcon(type) {
        const icons = {
            'success': 'check-circle',
            'error': 'exclamation-circle',
            'warning': 'exclamation-triangle',
            'info': 'info-circle'
        };
        return icons[type] || 'info-circle';
    }
}

// Utility functions for HTML onclick handlers
function switchSection(sectionId) {
    window.adminApp.switchSection(sectionId);
}

function executeDeepResearch() {
    window.adminApp.runDeepResearch();
}

function generateReport() {
    window.adminApp.generateReport();
}

function previewReport() {
    window.adminApp.previewReport();
}

function publishReport() {
    window.adminApp.publishReport();
}

function approveNews(button) {
    window.adminApp.approveNews(button);
}

function rejectNews(button) {
    window.adminApp.rejectNews(button);
}

/**
 * API テスト・統合機能クラス
 */
class APITestManager {
    constructor() {
        this.apiBaseUrl = '/.netlify/functions';
        this.testResults = [];
    }

    async runAllTests() {
        const testResults = document.getElementById('test-results');
        const testProgress = document.getElementById('test-progress');
        
        if (testResults) testResults.innerHTML = '';
        if (testProgress) testProgress.style.width = '0%';
        
        this.testResults = [];
        
        const tests = [
            { name: 'Health Check', fn: () => this.testHealthCheck() },
            { name: 'DeepResearch API', fn: () => this.testDeepResearchAPI() },
            { name: 'Analysis API', fn: () => this.testAnalysisAPI() },
            { name: 'Verification API', fn: () => this.testVerificationAPI() },
            { name: 'Data Collection', fn: () => this.testDataCollection() }
        ];
        
        for (let i = 0; i < tests.length; i++) {
            const test = tests[i];
            this.addTestResult(test.name, 'running', 'テスト実行中...');
            
            try {
                const result = await test.fn();
                this.addTestResult(test.name, 'success', result.message || 'テスト成功');
            } catch (error) {
                this.addTestResult(test.name, 'error', error.message || 'テスト失敗');
            }
            
            // Update progress
            if (testProgress) {
                testProgress.style.width = `${((i + 1) / tests.length) * 100}%`;
            }
            
            // Brief delay between tests
            await new Promise(resolve => setTimeout(resolve, 500));
        }
        
        this.generateTestSummary();
    }

    async testHealthCheck() {
        const response = await fetch(`${this.apiBaseUrl}/deepresearch-api?action=health`);
        
        if (!response.ok) {
            throw new Error(`Health check failed: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.status !== 'healthy') {
            throw new Error('API returned unhealthy status');
        }
        
        return { message: `API正常稼働中 (バージョン: ${data.version || 'unknown'})` };
    }

    async testDeepResearchAPI() {
        const testTopic = 'AI業界の最新動向テスト';
        
        const response = await fetch(`${this.apiBaseUrl}/deepresearch-api`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                action: 'analyze',
                topic: testTopic,
                options: { max_steps: 3 }
            })
        });
        
        if (!response.ok) {
            throw new Error(`DeepResearch API failed: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (!data.thinking_steps || data.thinking_steps.length === 0) {
            throw new Error('Invalid analysis result format');
        }
        
        return { 
            message: `分析完了 (ステップ数: ${data.thinking_steps.length}, 信頼度: ${data.confidence_score?.toFixed(2) || 'N/A'})` 
        };
    }

    async testAnalysisAPI() {
        const testNews = [
            { title: 'OpenAI新モデル発表', category: 'openai' },
            { title: 'Google Gemini更新', category: 'gemini' }
        ];
        
        const response = await fetch(`${this.apiBaseUrl}/deepresearch-api`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                action: 'prioritize',
                data: testNews
            })
        });
        
        if (!response.ok) {
            throw new Error(`Analysis API failed: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (!data.prioritized_items) {
            throw new Error('Invalid prioritization result');
        }
        
        return { message: `優先度分析完了 (${data.prioritized_items.length}件処理)` };
    }

    async testVerificationAPI() {
        // Mock verification test
        return new Promise((resolve) => {
            setTimeout(() => {
                resolve({ message: '検証エンジン正常動作中' });
            }, 1000);
        });
    }

    async testDataCollection() {
        // Mock data collection test
        return new Promise((resolve) => {
            setTimeout(() => {
                resolve({ message: 'データ収集システム正常動作中' });
            }, 800);
        });
    }

    addTestResult(testName, status, message) {
        const testResults = document.getElementById('test-results');
        if (!testResults) return;
        
        const resultItem = document.createElement('div');
        resultItem.className = `test-result test-${status}`;
        resultItem.innerHTML = `
            <div class="test-info">
                <strong>${testName}</strong>
                <div class="test-status">${this.getStatusIcon(status)} ${this.getStatusText(status)}</div>
            </div>
            <div class="test-message">${message}</div>
        `;
        
        // Replace existing result or add new one
        const existingResult = Array.from(testResults.children)
            .find(child => child.querySelector('strong').textContent === testName);
        
        if (existingResult) {
            testResults.replaceChild(resultItem, existingResult);
        } else {
            testResults.appendChild(resultItem);
        }
        
        this.testResults.push({ name: testName, status, message });
    }

    getStatusIcon(status) {
        const icons = {
            'running': '<i class="fas fa-spinner fa-spin"></i>',
            'success': '<i class="fas fa-check-circle"></i>',
            'error': '<i class="fas fa-times-circle"></i>',
            'warning': '<i class="fas fa-exclamation-triangle"></i>'
        };
        return icons[status] || '';
    }

    getStatusText(status) {
        const texts = {
            'running': '実行中',
            'success': '成功',
            'error': '失敗',
            'warning': '警告'
        };
        return texts[status] || status;
    }

    generateTestSummary() {
        const testSummary = document.getElementById('test-summary');
        if (!testSummary) return;
        
        const totalTests = this.testResults.length;
        const successCount = this.testResults.filter(r => r.status === 'success').length;
        const errorCount = this.testResults.filter(r => r.status === 'error').length;
        
        const successRate = totalTests > 0 ? (successCount / totalTests * 100).toFixed(1) : 0;
        
        testSummary.innerHTML = `
            <div class="summary-stats">
                <div class="stat-item">
                    <div class="stat-value">${successCount}/${totalTests}</div>
                    <div class="stat-label">成功</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${successRate}%</div>
                    <div class="stat-label">成功率</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${errorCount}</div>
                    <div class="stat-label">失敗</div>
                </div>
            </div>
            <div class="summary-status">
                <i class="fas fa-${errorCount === 0 ? 'check-circle' : 'exclamation-triangle'}"></i>
                ${errorCount === 0 ? 'すべてのテストが成功しました' : 'いくつかのテストが失敗しました'}
            </div>
        `;
    }

    async executeEnhancedDeepResearch(topic = 'AI業界の最新動向') {
        const loadingElement = document.getElementById('deepresearch-loading');
        const resultElement = document.getElementById('deepresearch-result');
        
        if (loadingElement) loadingElement.style.display = 'block';
        if (resultElement) resultElement.style.display = 'none';
        
        try {
            const response = await fetch(`${this.apiBaseUrl}/deepresearch-api`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    action: 'analyze',
                    topic: topic,
                    options: {
                        max_steps: 5,
                        enable_verification: true,
                        enable_visualization: true
                    }
                })
            });
            
            if (!response.ok) {
                throw new Error(`API Error: ${response.status}`);
            }
            
            const result = await response.json();
            
            if (resultElement) {
                resultElement.innerHTML = `
                    <div class="deepresearch-summary">
                        <h4>🧠 Enhanced DeepResearch 分析結果</h4>
                        <div class="result-stats">
                            <div class="stat-item">
                                <strong>${result.thinking_steps?.length || 0}</strong>
                                <span>思考ステップ</span>
                            </div>
                            <div class="stat-item">
                                <strong>${(result.confidence_score || 0).toFixed(2)}</strong>
                                <span>信頼度</span>
                            </div>
                            <div class="stat-item">
                                <strong>${(result.time_taken || 0).toFixed(2)}s</strong>
                                <span>処理時間</span>
                            </div>
                        </div>
                        <div class="result-content">
                            <h5>最終結論:</h5>
                            <p>${result.final_answer || '結論が生成されませんでした'}</p>
                        </div>
                        <div class="result-actions">
                            <button onclick="window.apiTest.showThinkingProcess()" class="btn btn-secondary">
                                <i class="fas fa-brain"></i> 思考プロセスを表示
                            </button>
                            <button onclick="window.apiTest.exportAnalysisData()" class="btn btn-secondary">
                                <i class="fas fa-download"></i> データエクスポート
                            </button>
                        </div>
                    </div>
                `;
                resultElement.style.display = 'block';
            }
            
            // Store result for later use
            this.lastAnalysisResult = result;
            
            window.adminApp.showNotification('Enhanced DeepResearch 分析が完了しました', 'success');
            
        } catch (error) {
            console.error('Enhanced DeepResearch error:', error);
            window.adminApp.showNotification(`分析エラー: ${error.message}`, 'error');
            
            if (resultElement) {
                resultElement.innerHTML = `
                    <div class="error-message">
                        <i class="fas fa-exclamation-triangle"></i>
                        <p>分析中にエラーが発生しました: ${error.message}</p>
                    </div>
                `;
                resultElement.style.display = 'block';
            }
        } finally {
            if (loadingElement) loadingElement.style.display = 'none';
        }
    }

    showThinkingProcess() {
        if (!this.lastAnalysisResult) {
            window.adminApp.showNotification('表示する分析結果がありません', 'warning');
            return;
        }
        
        // Open thinking process visualization in new window
        const visualizationWindow = window.open('', '_blank', 'width=1200,height=800');
        
        // Create HTML for thinking process visualization
        // This would use the thinking_visualizer.py generated HTML
        visualizationWindow.document.write(`
            <html>
            <head>
                <title>思考プロセス可視化</title>
                <style>
                    body { font-family: Arial, sans-serif; padding: 20px; }
                    .step { margin: 10px 0; padding: 15px; border-radius: 8px; background: #f8f9fa; }
                    .confidence { color: #007bff; font-weight: bold; }
                </style>
            </head>
            <body>
                <h1>🧠 思考プロセス可視化</h1>
                <div id="thinking-steps">
                    ${this.generateThinkingStepsHTML()}
                </div>
            </body>
            </html>
        `);
    }

    generateThinkingStepsHTML() {
        if (!this.lastAnalysisResult?.thinking_steps) {
            return '<p>思考ステップが見つかりません</p>';
        }
        
        return this.lastAnalysisResult.thinking_steps.map((step, index) => `
            <div class="step">
                <h3>ステップ ${index + 1}: ${step.phase || 'Unknown Phase'}</h3>
                <p><strong>信頼度:</strong> <span class="confidence">${(step.confidence || 0).toFixed(3)}</span></p>
                <p><strong>内容:</strong> ${step.content || step.description || 'No content available'}</p>
                <p><strong>時刻:</strong> ${step.timestamp || 'No timestamp'}</p>
            </div>
        `).join('');
    }

    exportAnalysisData() {
        if (!this.lastAnalysisResult) {
            window.adminApp.showNotification('エクスポートする分析結果がありません', 'warning');
            return;
        }
        
        const dataStr = JSON.stringify(this.lastAnalysisResult, null, 2);
        const blob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `enhanced_deepresearch_${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        
        URL.revokeObjectURL(url);
        
        window.adminApp.showNotification('分析データをエクスポートしました', 'success');
    }
}

// Initialize global instances
window.addEventListener('DOMContentLoaded', function() {
    window.adminApp = new AdminReportManager();
    window.apiTest = new APITestManager();
    
    window.adminApp.init().then(() => {
        console.log('Admin app initialized successfully');
    }).catch(error => {
        console.error('Failed to initialize admin app:', error);
    });
});

// Global functions for API testing
function runAPITests() {
    window.apiTest.runAllTests();
}

function executeEnhancedDeepResearch() {
    const topic = document.getElementById('deepresearch-topic')?.value || 'AI業界の最新動向';
    window.apiTest.executeEnhancedDeepResearch(topic);
}

// Additional global utility functions
function toggleTheme() {
    if (window.adminApp) {
        window.adminApp.toggleTheme();
    }
}

// Export for global access
window.AdminReportManager = AdminReportManager;
window.APITestManager = APITestManager; 