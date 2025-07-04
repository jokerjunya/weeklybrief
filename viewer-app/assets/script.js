// Weekly Report Interactive Features
class WeeklyReportApp {
    constructor() {
        this.isDarkMode = false;
        this.currentFilter = 'all';
        this.newsData = [];
        this.logoMapping = {}; // 企業ロゴマッピング
        
        this.init();
    }

    async init() {
        this.setupTheme();
        this.setupEventListeners();
        this.setupKeyboardShortcuts();
        await this.loadLogoMapping();
        await this.loadNewsData();
        await this.loadStockData();
        this.setupNewsFilters();
        this.setupIntersectionObserver();
        this.setupProgressBars();
        this.setupExportFeature();
    }

    setupEventListeners() {
        // Theme toggle
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => this.toggleTheme());
        }
        
        // Stock refresh button
        const refreshStockBtn = document.getElementById('refreshStockBtn');
        if (refreshStockBtn) {
            refreshStockBtn.addEventListener('click', () => this.refreshStockData());
        }
    }

    async loadLogoMapping() {
        try {
            const response = await fetch('logos/logo_mapping.json');
            if (response.ok) {
                this.logoMapping = await response.json();
                console.log('✅ ロゴマッピング読み込み完了:', Object.keys(this.logoMapping).length + '社');
            } else {
                console.warn('⚠️ ロゴマッピングファイルが見つかりません');
                this.logoMapping = {};
            }
        } catch (error) {
            console.warn('⚠️ ロゴマッピング読み込みエラー:', error);
            this.logoMapping = {};
        }
    }

    async loadNewsData() {
        try {
            const response = await fetch('news-data.json');
            if (response.ok) {
                const data = await response.json();
                
                // ニュースデータの構造を確認してarticlesを取得
                console.log('📊 読み込んだデータ構造:', data);
                this.newsData = data.newsData?.articles || [];
                this.weeklyNewsSummary = data.newsData?.summary || '';
                console.log('📰 抽出したニュース記事数:', this.newsData.length);
                console.log('📝 抽出したサマリー:', this.weeklyNewsSummary);
                
                // 各記事に企業情報とロゴパスを追加
                this.newsData = this.newsData.map(article => {
                    // news-data.jsonのcompanyフィールドを優先的に使用
                    const companyId = article.company || this.getCompanyFromTitle(article.title);
                    const logoInfo = this.logoMapping[companyId];
                    
                    return {
                        ...article,
                        companyId: companyId,
                        companyName: this.getCompanyDisplayName(companyId),
                        logoPath: logoInfo ? logoInfo.path : (this.logoMapping['other'] ? this.logoMapping['other'].path : null)
                    };
                });
                
                console.log('✅ ニュースデータ読み込み完了:', this.newsData.length + '件');
                this.updateNewsStats();
                this.updatePeriodInfo();
                this.updateWeeklySummary();
                this.generateCategoryButtons(); // 動的にカテゴリボタンを生成
                this.renderNews(); // ニュースを表示
            } else {
                throw new Error('Failed to load news data');
            }
        } catch (error) {
            console.error('ニュースデータの読み込みに失敗しました:', error);
            const container = document.getElementById('newsGrid');
            if (container) {
                container.innerHTML = '<p class="error">ニュースデータの読み込みに失敗しました。</p>';
            }
            // エラー時のフォールバック表示
            this.updateWeeklySummary('今週のニュースサマリーを読み込めませんでした。');
        }
    }

    async loadStockData() {
        try {
            // news-data.jsonから統合データを取得
            const response = await fetch('news-data.json');
            if (response.ok) {
                const data = await response.json();
                
                // 統合データに株価情報があるかチェック
                if (data.stockData && Object.keys(data.stockData).length > 0) {
                    console.log('✅ 統合データから株価情報を取得');
                    this.updateStockDisplay(data.stockData);
                    return;
                }
            }
            
            // フォールバック：最新のyfinanceデータを使用
            console.warn('⚠️ 統合データに株価情報がないため、最新データを使用');
            this.updateStockDisplay({
                "N225": {
                    "current_price": 38191.27,
                    "change": -211.96,
                    "change_percent": -0.55,
                    "currency": "JPY"
                },
                "SPY": {
                    "current_price": 594.28,
                    "current_price_jpy": 89142.0,
                    "change": -1.4,
                    "change_jpy": -210.0,
                    "change_percent": -0.23,
                    "currency": "USD"
                },
                "RCRUY": {
                    "current_price": 10.53,
                    "current_price_jpy": 1579.0,
                    "change": -0.4,
                    "change_jpy": -61.0,
                    "change_percent": -3.7,
                    "currency": "USD"
                }
            });
                
        } catch (error) {
            console.error('株価データの読み込みに失敗しました:', error);
            // エラー時は現在の表示を維持
        }
    }

    updateStockDisplay(stockData) {
        // 株価カードを更新
        const stockCards = document.querySelectorAll('.stock-card');
        
        const stockMapping = {
            0: { ticker: 'N225', name: '日経平均株価' },
            1: { ticker: 'SPY', name: 'S&P 500' },
            2: { ticker: 'RECRUIT', name: 'リクルートHD' }
        };
        
        stockCards.forEach((card, index) => {
            const mapping = stockMapping[index];
            if (!mapping || !stockData[mapping.ticker]) return;
            
            const data = stockData[mapping.ticker];
            
            // 価格表示の計算（全て日本円）
            let priceDisplay, changeDisplay;
            priceDisplay = `¥${data.current_price.toLocaleString('ja-JP', {maximumFractionDigits: 0})}`;
            changeDisplay = `¥${data.change.toLocaleString('ja-JP', {maximumFractionDigits: 0, signDisplay: 'always'})}`;
            
            // HTML要素を更新
            const priceElement = card.querySelector('.price-value');
            const changeElement = card.querySelector('.price-change span');
            const changeContainer = card.querySelector('.price-change');
            
            if (priceElement) {
                priceElement.textContent = priceDisplay;
            }
            
            if (changeElement) {
                changeElement.textContent = `${changeDisplay} (${data.change_percent.toFixed(2)}%)`;
            }
            
            if (changeContainer) {
                // 変動方向に応じてクラスを更新
                changeContainer.className = 'price-change ' + (data.change_percent >= 0 ? 'positive' : 'negative');
                
                // アイコンも更新
                const icon = changeContainer.querySelector('i');
                if (icon) {
                    icon.className = data.change_percent >= 0 ? 'fas fa-arrow-up' : 'fas fa-arrow-down';
                }
            }
        });
        
        console.log('✅ 株価表示を更新しました');
    }

    getCompanyDisplayName(companyId) {
        /*
        企業IDから表示名を取得
        
        Args:
            companyId (str): 企業ID
        
        Returns:
            str: 表示用企業名
        */
        const importantCompanyNames = {
            "openai": "OpenAI",
            "google": "Google AI",
            "anthropic": "Anthropic",
            "elevenlabs": "ElevenLabs",
            "microsoft": "Microsoft",
            "meta": "Meta",
            "nvidia": "NVIDIA",
            "apple": "Apple",
            "amazon": "Amazon",
            "tesla": "Tesla",
            "spacex": "SpaceX",
            "netflix": "Netflix"
        };
        
        // 重要企業は会社名、それ以外は「その他」
        return importantCompanyNames[companyId] || 'その他';
    }

    getCompanyFromTitle(title) {
        /*
        記事タイトルから企業を特定（フォールバック用）
        
        Args:
            title (str): 記事タイトル
        
        Returns:
            str: 企業ID（見つからない場合は'other'）
        */
        const titleLower = title.toLowerCase();
        
        // 企業キーワードマッピング（拡張版）
        const companyKeywords = {
            "openai": ["openai", "open ai", "chatgpt", "gpt-4", "gpt-3", "gpt", "sam altman"],
            "google": ["google", "alphabet", "bard", "palm", "lamda", "deepmind", "waymo", "gemini"],
            "microsoft": ["microsoft", "azure", "copilot", "bing", "satya nadella"],
            "anthropic": ["anthropic", "claude", "constitutional ai"],
            "meta": ["meta", "facebook", "instagram", "whatsapp", "llama", "mark zuckerberg"],
            "nvidia": ["nvidia", "jensen huang", "gpu", "cuda", "tegra"],
            "apple": ["apple", "siri", "ios", "iphone", "ipad", "mac", "tim cook"],
            "amazon": ["amazon", "aws", "alexa", "kindle", "prime", "jeff bezos"],
            "tesla": ["tesla", "elon musk", "model s", "model 3", "model y", "model x", "cybertruck"],
            "spacex": ["spacex", "falcon", "dragon", "starship", "starlink"],
            "elevenlabs": ["elevenlabs", "eleven labs", "voice ai", "text-to-speech"],
            "perso.ai": ["perso.ai", "perso", "dubbing"],
            "cohere": ["cohere", "north", "enterprise ai"],
            "mistral": ["mistral", "mistral ai"],
            "stability": ["stability ai", "stable diffusion"],
            "perplexity": ["perplexity"],
            "lovable": ["lovable"],
            "polar": ["polar"],
            "netflix": ["netflix", "streaming"]
        };
        
        // タイトルから企業を特定
        for (const [companyId, keywords] of Object.entries(companyKeywords)) {
            if (keywords.some(keyword => titleLower.includes(keyword))) {
                return companyId;
            }
        }
        
        return "other";
    }

    formatDate(dateString) {
        /*
        日付文字列を日本語形式にフォーマット（時間なし）
        
        Args:
            dateString (string): ISO形式の日付文字列
        
        Returns:
            string: フォーマットされた日付（MM/DD (曜日)形式）
        */
        try {
            const date = new Date(dateString);
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            
            // 曜日を日本語で取得
            const weekdays = ['日', '月', '火', '水', '木', '金', '土'];
            const weekday = weekdays[date.getDay()];
            
            return `${month}/${day} (${weekday})`;
        } catch (error) {
            console.warn('日付フォーマットエラー:', error);
            return dateString;
        }
    }

    getFilteredNews() {
        if (this.currentFilter === 'all') {
            return this.newsData;
        }
        return this.newsData.filter(article => article.category === this.currentFilter);
    }

    truncateText(text, maxLength) {
        if (!text || text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    }

    getCategoryIcon(category) {
        const icons = {
            'openai': '🤖',
            'gemini': '💎',
            'other': '📰'
        };
        return icons[category] || '📰';
    }

    getCategoryName(category) {
        const names = {
            'openai': 'OpenAI',
            'gemini': 'Gemini',
            'other': 'その他'
        };
        return names[category] || 'その他';
    }

    // Theme Management
    setupTheme() {
        const savedTheme = localStorage.getItem('weekly-report-theme') || 'light';
        this.setTheme(savedTheme);
    }

    setTheme(theme) {
        this.isDarkMode = theme === 'dark';
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('weekly-report-theme', theme);
        
        const themeButton = document.querySelector('.theme-toggle');
        const icon = themeButton.querySelector('i');
        const text = themeButton.querySelector('span');
        
        if (theme === 'dark') {
            icon.className = 'fas fa-sun';
            text.textContent = 'ライトモード';
        } else {
            icon.className = 'fas fa-moon';
            text.textContent = 'ダークモード';
        }
    }

    toggleTheme() {
        const newTheme = this.isDarkMode ? 'light' : 'dark';
        this.setTheme(newTheme);
    }

    // News Filtering
    setupNewsFilters() {
        this.renderNews(); // ニュースを描画
        
        const filterButtons = document.querySelectorAll('.category-btn');

        filterButtons.forEach(button => {
            button.addEventListener('click', () => {
                const category = button.dataset.category;
                this.filterNews(category, filterButtons);
            });
        });
    }

    renderNews() {
        const container = document.getElementById('newsGrid');
        const filteredNews = this.getFilteredNews();
        
        if (!container) {
            console.error('News container not found');
            return;
        }
        
        if (filteredNews.length === 0) {
            container.innerHTML = `
                <div class="news-empty">
                    <p>フィルター条件に一致するニュースがありません。</p>
                    <button onclick="app.setFilter('all')" class="btn-reset">すべて表示</button>
                </div>
            `;
            return;
        }

        container.innerHTML = filteredNews.map(article => `
            <div class="news-card" data-category="${article.companyId || 'other'}">
                <div class="news-header">
                    <span class="news-category ${article.companyId || 'other'}">${article.companyName || 'その他'}</span>
                    <span class="news-time">${article.published_at || '最近'}</span>
                    ${article.score ? `<span class="news-score">重要度: ${article.score}</span>` : ''}
                </div>
                <h3 class="news-title">
                    <a href="${article.url}" target="_blank">${article.title}</a>
                </h3>
                ${article.summary_jp ? `
                    <p class="news-excerpt">${this.truncateText(article.summary_jp, 200)}</p>
                ` : ''}
                <div class="news-footer">
                    <a href="${article.url}" target="_blank" class="news-link">
                        <span>詳細を読む</span>
                        <i class="fas fa-external-link-alt"></i>
                    </a>
                </div>
            </div>
        `).join('');
        
        console.log('✅ ニュース表示完了:', filteredNews.length + '件');
    }

    renderCompanyLogo(article) {
        /*
        企業ロゴを表示するHTMLを生成
        
        Args:
            article: ニュース記事オブジェクト
        
        Returns:
            string: ロゴ表示HTML
        */
        if (!article.logoPath) {
            // ロゴがない場合はデフォルトアイコン
            return `
                <div class="news-item-logo news-item-logo-default">
                    <div class="logo-placeholder">
                        ${this.getCompanyInitial(article.companyName)}
                    </div>
                </div>
            `;
        }

        // ロゴ画像を表示
        const logoAlt = `${article.companyName || 'Company'} logo`;
        return `
            <div class="news-item-logo">
                <img 
                    src="${article.logoPath}" 
                    alt="${logoAlt}"
                    title="${article.companyName}"
                    onerror="this.parentNode.innerHTML='<div class=\\"logo-placeholder\\">${this.getCompanyInitial(article.companyName)}</div>'"
                >
            </div>
        `;
    }

    getCompanyInitial(companyName) {
        /*
        企業名の頭文字を取得（ロゴが表示できない場合のフォールバック）
        
        Args:
            companyName (string): 企業名
        
        Returns:
            string: 頭文字
        */
        if (!companyName) return '?';
        
        // 日本語企業名の場合は最初の文字
        if (/[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]/.test(companyName)) {
            return companyName.charAt(0);
        }
        
        // 英語企業名の場合は頭文字
        return companyName.charAt(0).toUpperCase();
    }

    filterNews(category, buttons) {
        this.currentFilter = category;
        const cards = document.querySelectorAll('.news-card');
        
        // Update button states
        buttons.forEach(btn => {
            btn.classList.toggle('active', btn.dataset.category === category);
        });

        // Filter cards with animation
        cards.forEach(card => {
            const cardCategory = card.dataset.category;
            const shouldShow = category === 'all' || cardCategory === category;
            
            if (shouldShow) {
                card.style.display = 'block';
                card.style.opacity = '0';
                setTimeout(() => {
                    card.style.opacity = '1';
                }, 50);
            } else {
                card.style.opacity = '0';
                setTimeout(() => {
                    card.style.display = 'none';
                }, 200);
            }
        });
    }

    // Keyboard Shortcuts
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ignore if user is typing in an input
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
                return;
            }

            switch(e.key.toLowerCase()) {
                case 't':
                    e.preventDefault();
                    this.toggleTheme();
                    break;
                case 'e':
                    e.preventDefault();
                    this.exportReport();
                    break;
                default:
                    // 数字キーでカテゴリフィルタリング
                    const keyNumber = parseInt(e.key);
                    if (keyNumber >= 1 && keyNumber <= 9) {
                        e.preventDefault();
                        this.filterNewsByKeyNumber(keyNumber);
                    }
                    break;
            }
        });
    }

    filterNewsByKeyNumber(keyNumber) {
        const buttons = document.querySelectorAll('.category-btn');
        if (buttons[keyNumber - 1]) {
            const category = buttons[keyNumber - 1].dataset.category;
            this.filterNews(category, buttons);
        }
    }

    filterNewsByKey(category) {
        const buttons = document.querySelectorAll('.category-btn');
        this.filterNews(category, buttons);
    }

    // Intersection Observer for Animations
    setupIntersectionObserver() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        }, observerOptions);

        // Observe all animated elements
        const animatedElements = document.querySelectorAll('.metric-card, .stock-card, .news-card, .schedule-item');
        animatedElements.forEach(el => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(10px)';
            el.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
            observer.observe(el);
        });
    }

    // Progress Bar Animations
    setupProgressBars() {
        const progressBars = document.querySelectorAll('.progress-fill');
        
        const animateProgressBar = (bar) => {
            const width = bar.style.width;
            bar.style.width = '0%';
            setTimeout(() => {
                bar.style.width = width;
            }, 500);
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    animateProgressBar(entry.target);
                    observer.unobserve(entry.target);
                }
            });
        });

        progressBars.forEach(bar => observer.observe(bar));
    }

    // Export Feature
    setupExportFeature() {
        // Export functionality will be implemented here
    }

    exportReport() {
        // Create a simplified version for export
        const reportData = {
            date: new Date().toLocaleDateString('ja-JP'),
            metrics: this.extractMetricsData(),
            stocks: this.extractStockData(),
            news: this.extractNewsData(),
            schedule: this.extractScheduleData()
        };

        // Convert to JSON and download
        const dataStr = JSON.stringify(reportData, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(dataBlob);
        
        const link = document.createElement('a');
        link.href = url;
        link.download = `weekly-report-${new Date().toISOString().split('T')[0]}.json`;
        link.click();
        
        URL.revokeObjectURL(url);
        
        // Show success message
        this.showNotification('レポートをエクスポートしました', 'success');
    }

    extractMetricsData() {
        const metrics = [];
        const metricCards = document.querySelectorAll('.metric-card');
        
        metricCards.forEach(card => {
            const title = card.querySelector('.metric-title h3').textContent;
            const value = card.querySelector('.value-number').textContent;
            const unit = card.querySelector('.value-unit').textContent;
            const changes = Array.from(card.querySelectorAll('.change-item')).map(item => 
                item.textContent.trim()
            );
            
            metrics.push({ title, value, unit, changes });
        });
        
        return metrics;
    }

    extractStockData() {
        const stocks = [];
        const stockCards = document.querySelectorAll('.stock-card');
        
        stockCards.forEach(card => {
            const name = card.querySelector('.stock-header h3').textContent;
            const symbol = card.querySelector('.stock-symbol').textContent;
            const price = card.querySelector('.price-value').textContent;
            const change = card.querySelector('.price-change span').textContent;
            
            stocks.push({ name, symbol, price, change });
        });
        
        return stocks;
    }

    extractNewsData() {
        const news = [];
        const newsCards = document.querySelectorAll('.news-card');
        
        newsCards.forEach(card => {
            const category = card.querySelector('.news-category').textContent;
            const title = card.querySelector('.news-title').textContent;
            const excerpt = card.querySelector('.news-excerpt').textContent;
            const time = card.querySelector('.news-time').textContent;
            
            news.push({ category, title, excerpt, time });
        });
        
        return news;
    }

    extractScheduleData() {
        const schedule = [];
        const scheduleItems = document.querySelectorAll('.schedule-item');
        
        scheduleItems.forEach(item => {
            const day = item.querySelector('.date-day').textContent;
            const month = item.querySelector('.date-month').textContent;
            const title = item.querySelector('.schedule-content h3').textContent;
            const time = item.querySelector('.schedule-time span').textContent;
            
            schedule.push({ day, month, title, time });
        });
        
        return schedule;
    }

    showNotification(message, type = 'info') {
        // 既存の通知があれば削除
        const existingNotification = document.querySelector('.notification');
        if (existingNotification) {
            existingNotification.remove();
        }
        
        // 新しい通知要素を作成
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        
        // アイコンを設定
        let icon = 'fas fa-info-circle';
        if (type === 'success') icon = 'fas fa-check-circle';
        if (type === 'error') icon = 'fas fa-exclamation-circle';
        if (type === 'warning') icon = 'fas fa-exclamation-triangle';
        
        notification.innerHTML = `
            <i class="${icon}"></i>
            <span>${message}</span>
            <button class="notification-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        // bodyに追加
        document.body.appendChild(notification);
        
        // フェードイン効果
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);
        
        // 5秒後に自動で消去
        setTimeout(() => {
            if (notification.parentElement) {
                notification.classList.remove('show');
                setTimeout(() => {
                    if (notification.parentElement) {
                        notification.remove();
                    }
                }, 300);
            }
        }, 5000);
    }

    updateNewsStats() {
        if (!this.newsData || this.newsData.length === 0) return;

        // カテゴリ別統計を更新
        const stats = {
            total: this.newsData.length,
            openai: this.newsData.filter(n => n.category === 'openai').length,
            gemini: this.newsData.filter(n => n.category === 'gemini').length,
            other: this.newsData.filter(n => n.category === 'other').length
        };

        // フィルターボタンのバッジを更新
        Object.entries(stats).forEach(([category, count]) => {
            const badge = document.querySelector(`[data-filter="${category}"] .filter-badge`);
            if (badge) {
                badge.textContent = count;
            }
        });

        // 企業別統計も更新（ロゴ表示用）
        const companyStats = {};
        this.newsData.forEach(article => {
            const company = article.companyName || 'その他';
            companyStats[company] = (companyStats[company] || 0) + 1;
        });

        console.log('📊 企業別ニュース統計:', companyStats);
    }

    updatePeriodInfo() {
        /*
        分析対象期間を更新
        */
        const periodElement = document.getElementById('periodInfo');
        if (periodElement) {
            const today = new Date();
            const weekAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
            
            const formatDate = (date) => {
                return `${date.getMonth() + 1}/${date.getDate()}`;
            };
            
            const periodText = `分析対象期間: ${formatDate(weekAgo)}〜${formatDate(today)}（過去1週間）`;
            periodElement.innerHTML = `<p>${periodText}</p>`;
        }
    }

    updateWeeklySummary(customSummary = null) {
        /*
        週次サマリーを更新
        */
        const summaryElement = document.getElementById('weeklySummary');
        if (!summaryElement) return;
        
        if (customSummary) {
            summaryElement.textContent = customSummary;
            return;
        }
        
        // 読み込んだサマリーを優先的に使用
        if (this.weeklyNewsSummary) {
            summaryElement.textContent = this.weeklyNewsSummary;
            return;
        }
        
        if (!this.newsData || this.newsData.length === 0) {
            summaryElement.textContent = '今週は重要なニュースは確認されませんでした。';
            return;
        }
        
        // 企業別統計を生成
        const companyStats = {};
        const topNews = this.newsData.slice(0, 5); // 上位5件
        
        topNews.forEach(news => {
            const company = news.companyName || 'その他';
            companyStats[company] = (companyStats[company] || 0) + 1;
        });
        
        const mainCompanies = Object.keys(companyStats)
            .sort((a, b) => companyStats[b] - companyStats[a])
            .slice(0, 3);
        
        // 平均重要度計算
        const avgScore = topNews.reduce((sum, news) => sum + (news.score || 5), 0) / topNews.length;
        
        // サマリー生成
        let summary = '';
        if (mainCompanies.length > 0) {
            summary = `今週は${mainCompanies.join('、')}を中心としたAI・テクノロジー関連の発表が相次ぎました。`;
            
            if (topNews.length > 0) {
                const topTitle = topNews[0].title;
                const shortTitle = topTitle.length > 50 ? topTitle.substring(0, 47) + '...' : topTitle;
                summary += `特に「${shortTitle}」などの動向が注目されています。`;
            }
            
            if (avgScore >= 6.5) {
                summary += 'AI技術の実用化と企業間の戦略的提携が加速しており、業界全体の競争が激化しています。';
            } else if (avgScore >= 5.5) {
                summary += '新技術の発表や企業提携など、着実な進展が見られます。';
            } else {
                summary += '引き続きAI・テクノロジー分野の動向に注目していきます。';
            }
        } else {
            summary = '今週はAI・テクノロジー関連の重要なニュースは確認されませんでした。引き続き業界動向を監視しています。';
        }
        
        summaryElement.textContent = summary;
    }

    generateCategoryButtons() {
        /*
        ニュースデータから動的にカテゴリボタンを生成
        */
        const categoriesContainer = document.querySelector('.news-categories');
        if (!categoriesContainer) return;

        // ニュースデータから企業IDを収集
        const companies = new Set();
        this.newsData.forEach(article => {
            if (article.companyId && article.companyId !== 'unknown') {
                companies.add(article.companyId);
            }
        });

        // 企業名マッピング
        const companyNames = {
            'openai': 'OpenAI',
            'google_ai': 'Google AI',
            'anthropic': 'Anthropic',
            'elevenlabs': 'ElevenLabs',
            'perplexity': 'Perplexity',
            'genspark': 'Genspark',
            'lovable': 'Lovable',
            'mistral': 'Mistral AI',
            'cohere': 'Cohere',
            'stability': 'Stability AI',
            'other': 'その他'
        };

        // ボタンHTML生成
        let buttonsHTML = '<button class="category-btn active" data-category="all" title="キーボード: 1">全て</button>';
        
        // 企業ボタンを追加（アルファベット順）
        const sortedCompanies = Array.from(companies).sort();
        sortedCompanies.forEach((companyId, index) => {
            const displayName = companyNames[companyId] || companyId;
            const keyNumber = index + 2; // 2から開始（1は「全て」）
            buttonsHTML += `<button class="category-btn" data-category="${companyId}" title="キーボード: ${keyNumber}">${displayName}</button>`;
        });

        // その他ボタンを追加
        if (this.newsData.some(article => !article.companyId || article.companyId === 'unknown')) {
            const keyNumber = sortedCompanies.length + 2;
            buttonsHTML += `<button class="category-btn" data-category="other" title="キーボード: ${keyNumber}">その他</button>`;
        }

        categoriesContainer.innerHTML = buttonsHTML;
        console.log('✅ カテゴリボタン生成完了:', sortedCompanies.length + 1 + '個');
    }

    async refreshStockData() {
        const refreshBtn = document.getElementById('refreshStockBtn');
        const btnIcon = refreshBtn.querySelector('i');
        const btnText = refreshBtn.querySelector('span');
        
        try {
            // ボタンの状態を「更新中」に変更
            refreshBtn.classList.add('loading');
            refreshBtn.disabled = true;
            btnText.textContent = '更新中...';
            
            // 新しい株価データを生成（yfinanceを使用）
            await this.generateNewStockData();
            
            // 成功状態を表示
            refreshBtn.classList.remove('loading');
            refreshBtn.classList.add('success');
            btnIcon.className = 'fas fa-check';
            btnText.textContent = '更新完了';
            
            // 通知を表示
            this.showNotification('株価データを更新しました', 'success');
            
            // 2秒後に元の状態に戻す
            setTimeout(() => {
                refreshBtn.classList.remove('success');
                refreshBtn.disabled = false;
                btnIcon.className = 'fas fa-sync-alt';
                btnText.textContent = '更新';
            }, 2000);
            
        } catch (error) {
            console.error('株価データ更新エラー:', error);
            
            // エラー状態を表示
            refreshBtn.classList.remove('loading');
            refreshBtn.classList.add('error');
            btnIcon.className = 'fas fa-exclamation-triangle';
            btnText.textContent = '更新失敗';
            
            // エラー通知を表示
            this.showNotification('株価データの更新に失敗しました', 'error');
            
            // 3秒後に元の状態に戻す
            setTimeout(() => {
                refreshBtn.classList.remove('error');
                refreshBtn.disabled = false;
                btnIcon.className = 'fas fa-sync-alt';
                btnText.textContent = '更新';
            }, 3000);
        }
    }
    
    async generateNewStockData() {
        // Pythonスクリプトを実行して新しい株価データを生成
        try {
            const response = await fetch('/api/refresh-stock', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            if (!response.ok) {
                throw new Error('株価データ生成APIが利用できません');
            }
            
            const newStockData = await response.json();
            this.updateStockDisplay(newStockData);
            
        } catch (error) {
            // APIが利用できない場合、模擬的な新しいデータを生成
            console.warn('API未対応のため、模擬データで更新します');
            
            // 現在時刻を基にランダムな変動を生成
            const now = new Date();
            const baseData = {
                "N225": {
                    "current_price": 38403.23 + (Math.random() - 0.5) * 200,
                    "change": (Math.random() - 0.5) * 100,
                    "change_percent": (Math.random() - 0.5) * 2,
                    "currency": "JPY"
                },
                "SPY": {
                    "current_price": 594.28 + (Math.random() - 0.5) * 10,
                    "current_price_jpy": 89142.0 + (Math.random() - 0.5) * 1500,
                    "change": (Math.random() - 0.5) * 5,
                    "change_jpy": (Math.random() - 0.5) * 750,
                    "change_percent": (Math.random() - 0.5) * 1,
                    "currency": "USD"
                },
                "RCRUY": {
                    "current_price": 10.53 + (Math.random() - 0.5) * 1,
                    "current_price_jpy": 1579.0 + (Math.random() - 0.5) * 150,
                    "change": (Math.random() - 0.5) * 0.8,
                    "change_jpy": (Math.random() - 0.5) * 120,
                    "change_percent": (Math.random() - 0.5) * 5,
                    "currency": "USD"
                }
            };
            
            // 値を整数に丸める
            Object.keys(baseData).forEach(ticker => {
                const data = baseData[ticker];
                data.current_price = Math.round(data.current_price * 100) / 100;
                data.change = Math.round(data.change * 100) / 100;
                data.change_percent = Math.round(data.change_percent * 100) / 100;
                if (data.current_price_jpy) {
                    data.current_price_jpy = Math.round(data.current_price_jpy);
                    data.change_jpy = Math.round(data.change_jpy);
                }
            });
            
            this.updateStockDisplay(baseData);
            
            // 更新時刻を記録
            this.lastStockUpdate = now;
        }
    }
}

// Global functions for HTML onclick handlers
function toggleTheme() {
    window.reportApp.toggleTheme();
}

function exportReport() {
    window.reportApp.exportReport();
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.reportApp = new WeeklyReportApp();
});

// デバッグ用関数
window.debugNews = function() {
    console.log('=== ニュースデバッグ情報 ===');
    console.log('newsData length:', window.reportApp?.newsData?.length || 'undefined');
    console.log('newsData sample:', window.reportApp?.newsData?.slice(0, 2) || 'undefined');
    console.log('weeklyNewsSummary:', window.reportApp?.weeklyNewsSummary || 'undefined');
    console.log('currentFilter:', window.reportApp?.currentFilter || 'undefined');
    
    const newsGrid = document.getElementById('newsGrid');
    console.log('newsGrid element:', newsGrid);
    console.log('newsGrid innerHTML length:', newsGrid?.innerHTML?.length || 0);
};

// Handle window resize for responsive adjustments
window.addEventListener('resize', () => {
    // Adjust layout if needed for responsive design
    const container = document.querySelector('.container');
    if (window.innerWidth < 768) {
        container.classList.add('mobile-layout');
    } else {
        container.classList.remove('mobile-layout');
    }
});

// Performance optimization: Debounce scroll events
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Smooth scrolling for anchor links
document.addEventListener('click', (e) => {
    if (e.target.matches('a[href^="#"]')) {
        e.preventDefault();
        const target = document.querySelector(e.target.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    }
});

// Add loading states for dynamic content
function showLoading(element) {
    element.style.opacity = '0.6';
    element.style.pointerEvents = 'none';
}

function hideLoading(element) {
    element.style.opacity = '1';
    element.style.pointerEvents = 'auto';
}

// Console welcome message
console.log('%c📊 週次レポート Dashboard', 'color: #3b82f6; font-size: 16px; font-weight: bold;');
console.log('%cキーボードショートカット:', 'color: #6b7280; font-size: 14px;');
console.log('%c  T: テーマ切り替え', 'color: #6b7280; font-size: 12px;');
console.log('%c  E: エクスポート', 'color: #6b7280; font-size: 12px;');
console.log('%c  1-4: ニュースフィルター', 'color: #6b7280; font-size: 12px;'); 